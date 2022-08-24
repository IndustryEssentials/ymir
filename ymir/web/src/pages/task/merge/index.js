import React, { useEffect, useState } from "react"
import { Button, Form, message, Card, Space, Radio, Input } from "antd"
import { useHistory, useLocation, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { string2Array } from '@/utils/string'
import useFetch from '@/hooks/useFetch'

import Breadcrumbs from "@/components/common/breadcrumb"
import DatasetSelect from "@/components/form/datasetSelect"
import Desc from "@/components/form/desc"

import commonStyles from "../common.less"
import s from "./index.less"
import MergeType from "./components/formItem.mergeType"
import DatasetName from "../../../components/form/items/datasetName"
import Strategy from "./components/formItem.strategy"

const { useWatch, useForm } = Form

function Merge() {
  const [dataset, getDataset] = useFetch('dataset/getDataset', {})
  const [_, clearCache] = useFetch('dataset/clearCache')
  const [mergeResult, merge] = useFetch('task/merge')
  const [__, updateIteration] = useFetch('iteration/updateIteration')
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const { query } = useLocation()
  const { iterationId, currentStage, outputKey, } = query
  const did = Number(query.did)
  const mid = string2Array(query.mid)
  const history = useHistory()
  const [form] = useForm()
  const includes = useWatch('includes', form)
  const excludes = useWatch('excludes', form)
  const type = useWatch('type', form)
  const selectedDataset = useWatch('dataset', form)


  const initialValues = {
    includes: mid,
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
      return message.error(t('dataset.merge.validate.inputs'))
    }
    const params = {
      ...values,
      projectId: pid,
      datasets: [did, selectedDataset, ...values.includes].filter(item => item),
    }
    await merge(params)
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function filter(datasets, ids = []) {
    return datasets.filter(ds => ![...ids, did].includes(ds.id))
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
          <MergeType initialValue={mid ? 0 : 1} />
          {did ? <Form.Item label={t('task.fusion.form.dataset')}>
            <span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span>
          </Form.Item> : null}
          {type ? <Form.Item name='dataset' label={t('task.fusion.form.dataset')}>
            <DatasetSelect
              pid={pid}
              filters={datasets => filter(datasets, [...(includes || []), ...(excludes || [])])}
            />
          </Form.Item> : <DatasetName />}
          <Form.Item label={t('task.fusion.form.merge.include.label')} name="includes" tooltip={t('tip.task.merge.include')}>
            <DatasetSelect
              placeholder={t('task.fusion.form.datasets.placeholder')}
              mode='multiple'
              pid={pid}
              filters={datasets => filter(datasets, [selectedDataset, ...(excludes || [])])}
              allowEmpty={true}
              showArrow
            />
          </Form.Item>
          <Strategy hidden={includes?.length < 1} />
          <Form.Item label={t('task.fusion.form.merge.exclude.label')} name="excludes" tooltip={t('tip.task.merge.exclude')}>
            <DatasetSelect
              placeholder={t('task.fusion.form.datasets.placeholder')}
              mode='multiple'
              pid={pid}
              filters={datasets => filter(datasets, [selectedDataset, ...(includes || [])])}
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
