import React, { useEffect } from "react"
import { Button, Form, message, Card, Space, Radio } from "antd"
import { useHistory, useLocation, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'

import Breadcrumbs from "@/components/common/breadcrumb"
import DatasetSelect from "@/components/form/datasetSelect"
import Desc from "@/components/form/desc"

import commonStyles from "../common.less"
import s from "./index.less"

function Merge() {
  const [dataset, getDataset] = useFetch('dataset/getDataset', {})
  const [_, clearCache] = useFetch('dataset/clearCache')
  const [mergeResult, merge] = useFetch('task/merge')
  const [__, updateIteration] = useFetch('iteration/updateIteration')
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const { query } = useLocation()
  const { iterationId, currentStage, outputKey, merging } = query
  const did = Number(query.did)
  const history = useHistory()
  const [form] = Form.useForm()
  const includes = Form.useWatch('includes', form)
  const excludes = Form.useWatch('excludes', form)


  const initialValues = {
    includes: Number(merging) ? [Number(merging)] : [],
    strategy: 2,
  }

  useEffect(() => {
    did && getDataset({ id: did })
  }, [did])

  useEffect(() => {
    if (mergeResult) {
      if (iterationId) {
        updateIteration({ id: iterationId, currentStage, [outputKey]: mergeResult.id })
      }
      message.info(t('task.fusion.create.success.msg'))
      clearCache()
      const group = mergeResult.dataset_group_id || ''
      history.replace(`/home/project/${dataset.projectId}/dataset#${group}`)
    }
  }, [mergeResult])

  const checkInputs = (i) => {
    return i?.excludes?.length || i?.includes?.length
  }

  const onFinish = async (values) => {
    if (!checkInputs(values)) {
      return message.error(t('dataset.fusion.validate.inputs'))
    }
    const params = {
      ...values,
      projectId: dataset.projectId,
      dataset: did,
    }
    await merge(params)
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function filterExcludes(datasets) {
    return datasets.filter(ds => ![...(includes || []), did].includes(ds.id))
  }

  function filterIncludes(datasets) {
    return datasets.filter(ds => ![...(excludes || []), did].includes(ds.id))
  }

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('task.fusion.header.merge')}>
        <Form
          form={form}
          name='mergeForm'
          {...formLayout}
          initialValues={initialValues}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
        >
          <Form.Item label={t('task.fusion.form.dataset')}>
            <span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span>
          </Form.Item>
          <Form.Item label={t('task.fusion.form.merge.include.label')} name="includes" tooltip={'tip.task.merge.include'}>
            <DatasetSelect
              placeholder={t('task.fusion.form.datasets.placeholder')}
              mode='multiple'
              pid={pid}
              filters={filterIncludes}
              allowEmpty={true}
              showArrow
            />
          </Form.Item>
          <Form.Item name='strategy'
            hidden={includes?.length < 1}
            label={t('task.train.form.repeatdata.label')} initialValue={2}>
            <Radio.Group options={[
              { value: 2, label: t('task.train.form.repeatdata.latest') },
              { value: 3, label: t('task.train.form.repeatdata.original') },
              { value: 1, label: t('task.train.form.repeatdata.terminate') },
            ]} />
          </Form.Item>
          <Form.Item label={t('task.fusion.form.merge.exclude.label')} name="excludes" tooltip={'tip.task.merge.exclude'}>
            <DatasetSelect
              placeholder={t('task.fusion.form.datasets.placeholder')}
              mode='multiple'
              pid={pid}
              filters={filterExcludes}
              showArrow
            />
          </Form.Item>
          <Desc form={form} />
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

export default Merge
