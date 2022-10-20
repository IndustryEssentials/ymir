import React, { useEffect, useState } from "react"
import { Form, message } from "antd"
import { useHistory, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'

import DatasetSelect from "@/components/form/datasetSelect"
import Desc from "@/components/form/desc"
import MergeType from "./merge/formItem.mergeType"
import DatasetName from "@/components/form/items/datasetName"
import Strategy from "./merge/formItem.strategy"

import s from "./merge/merge.less"

const { useWatch, useForm } = Form

function Merge({ query = {}, hidden, ok = () => { }, bottom, }) {
  const [dataset, getDataset, setDataset] = useFetch('dataset/getDataset', {})
  const [_, clearCache] = useFetch('dataset/clearCache')
  const [mergeResult, merge] = useFetch('task/merge')
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const { did, mid, iterationId, currentStage, outputKey, } = query
  const history = useHistory()
  const [form] = useForm()
  const [group, setGroup] = useState()
  const includes = useWatch('includes', form)
  const excludes = useWatch('excludes', form)
  const type = useWatch('type', form)
  const selectedDataset = useWatch('dataset', form)


  const initialValues = {
    includes: Array.isArray(mid) ? mid : [mid],
  }

  useEffect(() => {
    did && getDataset({ id: did })
  }, [did])

  useEffect(() => dataset.id && setGroup(dataset.groupId), [dataset])

  useEffect(() => {
    if (mergeResult) {
      ok(mergeResult)
      message.info(t('task.fusion.create.success.msg'))
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
      group: type ? group : undefined,
      projectId: pid,
      datasets: [did, selectedDataset, ...(values.includes || [])].filter(item => item),
    }
    await merge(params)
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  function filter(datasets, ids = []) {
    return datasets.filter(ds => ![...ids, did].includes(ds.id))
  }

  function originDatasetChange(_, option) {
    setDataset(option?.dataset || {})
    setGroup(option?.dataset?.groupId || undefined)
  }

  return (
    <Form
      form={form}
      name='mergeForm'
      {...formLayout}
      initialValues={initialValues}
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
    >
      <div hidden={hidden}>
        <MergeType disabled={[iterationId ? 0 : null]} initialValue={!iterationId && mid ? 0 : 1} />
        {!type ? <DatasetName /> : null}
        {did ? <Form.Item label={t('task.fusion.form.dataset')}>
          <span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span>
        </Form.Item> : null}
        {!did && (type || dataset.id) ? <Form.Item name='dataset' label={t('task.fusion.form.dataset')}>
          <DatasetSelect
            pid={pid}
            onChange={originDatasetChange}
            filters={datasets => filter(datasets, [...(includes || []), ...(excludes || [])])}
          />
        </Form.Item> : null}
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
      </div>
      <Form.Item className={s.submit} wrapperCol={{ offset: 8 }}>
        {bottom ? bottom : <SubmitButtons />}
      </Form.Item>
    </Form>
  )
}

export default Merge
