import React, { useState, useEffect, useCallback } from "react"
import { Button, Form, message, Card, Space, InputNumber } from "antd"
import { useHistory, useLocation, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import s from "./index.less"
import commonStyles from "../common.less"
import RecommendKeywords from "@/components/common/recommendKeywords"
import useFetch from '@/hooks/useFetch'
import Desc from "@/components/form/desc"
import KeywordSelect from "@/components/form/keywordSelect"

function Filter() {
  const { query } = useLocation()
  const did = Number(query.did)
  const history = useHistory()
  const [form] = Form.useForm()
  const [keywords, setKeywords] = useState([])
  const [dataset, getDataset] = useFetch('dataset/getDataset', {})
  const [filterResult, filter] = useFetch('task/filter')
  const [_, clearCache] = useFetch('dataset/clearCache')
  const includes = Form.useWatch('includes', form)
  const excludes = Form.useWatch('excludes', form)

  useEffect(() => {
    did && getDataset({ id: did })
  }, [did])

  useEffect(() => {
    if (dataset?.id) {
      setKeywords(dataset.keywords)
    }
  }, [dataset])

  useEffect(() => {
    if (filterResult) {
      message.info(t('task.fusion.create.success.msg'))
      clearCache()
      const group = mergeResult.dataset_group_id || ''
      history.replace(`/home/project/${dataset.projectId}/dataset#${group}`)
    }
  }, [filterResult])

  const checkInputs = (i) => {
    return i.excludes?.length || i.includes?.length || i.samples
  }

  const onFinish = (values) => {
    if (!checkInputs(values)) {
      return message.error(t('dataset.fusion.validate.inputs'))
    }
    const params = {
      ...values,
      projectId: dataset.projectId,
      dataset: did,
    }
    filter(params)
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function selectRecommendKeywords(keyword) {
    const kws = [...new Set([...(includes || []), keyword])]
    form.setFieldsValue({ includes: kws })
  }

  const filterExcludes = useCallback(options => {
    return options.filter(({ value }) => !(includes || []).includes(value))
  }, [includes])

  const filterIncludes = useCallback(options => {
    return options.filter(({ value }) => !(excludes || []).includes(value))
  }, [excludes])

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('task.fusion.header.filter')}>
        <Form
          form={form}
          name='fusionForm'
          {...formLayout}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
        >
          <Form.Item label={t('task.fusion.form.dataset')}>
            <span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span>
          </Form.Item>
          <Form.Item
            label={t('task.fusion.form.include.label')}
            tooltip={t('tip.task.fusion.includelable')}
            name='includes'
            help={<RecommendKeywords sets={did} onSelect={selectRecommendKeywords} />}
          >
            <KeywordSelect mode="multiple" keywords={keywords} filter={filterIncludes} placeholder={t('task.filter.includes.placeholder')} />
          </Form.Item>
          <Form.Item
            label={t('task.fusion.form.exclude.label')}
            tooltip={t('tip.task.fusion.excludelable')}
            name='excludes'
          >
            <KeywordSelect mode="multiple" keywords={keywords} filter={filterExcludes} placeholder={t('task.filter.excludes.placeholder')} />
          </Form.Item>
          <Form.Item
            label={t('task.fusion.form.sampling')}
            tooltip={t('tip.task.fusion.sampling')}
            name='samples'
          >
            <InputNumber step={1} min={1} precision={0} style={{ width: '100%' }} />
          </Form.Item>
          <Desc />
          <Form.Item className={s.submit} wrapperCol={{ offset: 8 }}>
            <Space size={20}>
              <Form.Item name='submitBtn' noStyle>
                <Button type="primary" size="large" htmlType="submit">
                  {t('common.confirm')}
                </Button>
              </Form.Item>
              <Form.Item name='backBtn' noStyle>
                <Button size="large" onClick={() => history.goBack()}>
                  {t('task.btn.back')}
                </Button>
              </Form.Item>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default Filter
