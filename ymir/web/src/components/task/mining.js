import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Card, Radio, Button, Form, ConfigProvider, Space, InputNumber } from "antd"
import { useHistory, useParams, useLocation } from "umi"


import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { HIDDENMODULES } from '@/constants/common'
import { string2Array } from '@/utils/string'
import { OPENPAI_MAX_GPU_COUNT } from '@/constants/common'
import { TYPES } from '@/constants/image'
import { randomNumber } from "@/utils/number"
import useFetch from '@/hooks/useFetch'

import ModelSelect from "@/components/form/modelSelect"
import ImageSelect from "@/components/form/imageSelect"
import DatasetSelect from "@/components/form/datasetSelect"
import LiveCodeForm from "@/components/form/items/liveCode"
import { removeLiveCodeConfig } from "@/components/form/items/liveCodeConfig"
import DockerConfigForm from "@/components/form/items/dockerConfig"
import OpenpaiForm from "@/components/form/items/openpai"
import Desc from "@/components/form/desc"

import styles from "./mining.less"
import SubmitButtons from "./submitButtons"

function Mining({ query = {}, hidden, ok = () => { }, datasetCache, bottom, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { mid, image, iterationId, currentStage, outputKey } = query
  const stage = mid
  const did = Number(query.did)
  const [dataset, setDataset] = useState({})
  const [selectedModel, setSelectedModel] = useState({})
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState({})
  const [topk, setTopk] = useState(true)
  const [gpu_count, setGPU] = useState(0)
  const [imageHasInference, setImageHasInference] = useState(false)
  const [live, setLiveCode] = useState(false)
  const [openpai, setOpenpai] = useState(false)
  const [sys, getSysInfo] = useFetch('common/getSysInfo', {})
  const selectOpenpai = Form.useWatch('openpai', form)
  const [showConfig, setShowConfig] = useState(false)

  useEffect(() => {
    getSysInfo()
  }, [])

  useEffect(() => {
    setGPU(sys.gpu_count || 0)
    if (!HIDDENMODULES.OPENPAI) {
      setOpenpai(!!sys.openpai_enabled)
    }
  }, [sys])

  useEffect(() => {
    setGPU(selectOpenpai ? OPENPAI_MAX_GPU_COUNT : sys.gpu_count || 0)
  }, [selectOpenpai])

  useEffect(() => {
    did && func.getDataset(did)
  }, [did])

  useEffect(() => {
    const cache = datasetCache[did]
    if (cache) {
      setDataset(cache)
    }
  }, [datasetCache])

  useEffect(() => {
    const state = location.state

    if (state?.record) {
      const { task: { parameters, config }, description, } = state.record
      const {
        dataset_id,
        docker_image,
        docker_image_id,
        model_id,
        model_stage_id,
        top_k,
        generate_annotations,
      } = parameters
      form.setFieldsValue({
        datasetId: dataset_id,
        gpu_count: config.gpu_count,
        modelStage: [model_id, model_stage_id],
        image: docker_image_id + ',' + docker_image,
        topk: top_k,
        inference: generate_annotations,
        description,
      })
      setShowConfig(true)

      setTimeout(() => setConfig(config), 500)

      history.replace({ state: {} })
    }
  }, [location.state])

  function imageChange(_, image = {}) {
    const { url, configs = [] } = image
    const configObj = configs.find(conf => conf.type === TYPES.MINING) || {}
    const hasInference = configs.some(conf => conf.type === TYPES.INFERENCE)
    setImageHasInference(hasInference)
    !hasInference && form.setFieldsValue({ inference: false })
    if (!HIDDENMODULES.LIVECODE) {
      setLiveCode(image.liveCode || false)
    }
    setConfig(removeLiveCodeConfig(configObj.config))
  }

  function setConfig(config = {}) {
    setSeniorConfig(config)
  }

  const onFinish = async (values) => {
    const config = {
      ...values.hyperparam?.reduce(
        (prev, { key, value }) => key && value ? { ...prev, [key]: value } : prev,
        {}),
      ...(values.live || {}),
    }

    config['gpu_count'] = form.getFieldValue('gpu_count') || 0

    const img = (form.getFieldValue('image') || '').split(',')
    const imageId = Number(img[0])
    const image = img[1]
    const params = {
      ...values,
      name: 'task_mining_' + randomNumber(),
      projectId: pid,
      imageId,
      image,
      config,
    }
    const result = await func.mine(params)
    result && ok(result.result_dataset)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function setsChange(id, option) {
    setDataset(option?.dataset || {})
  }

  function modelChange(stage, options) {
    if (stage && !stage[1] && options && options[1]) {
      form.setFieldsValue({ modelStage: [stage[0], options[1]] })
    }
    setSelectedModel(options ? options[0].model : [])
  }

  const initialValues = {
    modelStage: stage,
    image: image ? parseInt(image) : undefined,
    datasetId: did ? did : undefined,
    topk: 0,
    gpu_count: 0,
  }
  return (
    <div>
      <Form
        className={styles.form}
        {...formLayout}
        form={form}
        name='miningForm'
        initialValues={initialValues}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
      >
        <div hidden={hidden}>
          <Form.Item name='image' tooltip={t('tip.task.mining.image')} label={t('task.mining.form.image.label')} rules={[
            { required: true, message: t('task.train.form.image.required') }
          ]}>
            <ImageSelect placeholder={t('task.train.form.image.placeholder')}
              relatedId={selectedModel?.task?.parameters?.docker_image_id} type={TYPES.MINING} onChange={imageChange} />
          </Form.Item>
          <OpenpaiForm form={form} openpai={openpai} />
          <Form.Item
            label={t('task.mining.form.dataset.label')}
            tooltip={t('tip.task.mining.dataset')}
            required
            name="datasetId"
            rules={[
              { required: true, message: t('task.mining.form.dataset.required') },
            ]}
          >
            <DatasetSelect
              pid={pid}
              placeholder={t('task.mining.form.dataset.placeholder')}
              onChange={setsChange}
            />
          </Form.Item>
          <Form.Item
            label={t('task.mining.form.model.label')}
            tooltip={t('tip.task.filter.model')}
            name="modelStage"
            rules={[
              { required: true, message: t('task.mining.form.model.required') },
            ]}
          >
            <ModelSelect placeholder={t('task.mining.form.mining.model.required')} onChange={modelChange} pid={pid} />
          </Form.Item>
          <Form.Item
            tooltip={t('tip.task.filter.strategy')}
            label={t('task.mining.form.topk.label')}
            name='topk' rules={topk ? [
              { type: 'number', min: 1, max: (dataset.assetCount - 1) || 1 }
            ] : null}>
            <InputNumber style={{ width: 120 }} min={1} max={dataset.assetCount - 1} precision={0} />
          </Form.Item>
          <Form.Item
            tooltip={t('tip.task.filter.newlable')}
            label={t('task.mining.form.label.label')}
            name='inference'
            initialValue={imageHasInference}
          >
            <Radio.Group options={[
              { value: true, label: t('common.yes'), disabled: !imageHasInference },
              { value: false, label: t('common.no') },
            ]} />
          </Form.Item>

          <Form.Item
            tooltip={t('tip.task.filter.mgpucount')}
            label={t('task.gpu.count')}
          >
            <Form.Item
              noStyle
              name="gpu_count"
              rules={[
                {
                  validator: (rules, value) => value <= gpu_count ?
                    Promise.resolve() :
                    Promise.reject(),
                  message: t('task.gpu.tip', { count: gpu_count })
                }
              ]}
            >
              <InputNumber min={0} max={gpu_count} precision={0} /></Form.Item>
            <span style={{ marginLeft: 20 }}>{t('task.gpu.tip', { count: gpu_count })}</span>
          </Form.Item>

          <LiveCodeForm form={form} live={live} />
          <DockerConfigForm form={form} show={showConfig} seniorConfig={seniorConfig} />
          <Desc form={form} />
        </div>
        <Form.Item wrapperCol={{ offset: 8 }}>
          {bottom ? bottom : <SubmitButtons label="common.action.mining" />}
        </Form.Item>
      </Form>
    </div>
  )
}

const props = (state) => {
  return {
    datasetCache: state.dataset.dataset,
  }
}

const dis = (dispatch) => {
  return {
    getSysInfo() {
      return dispatch({
        type: "common/getSysInfo",
      })
    },
    getDatasets(pid, force = true) {
      return dispatch({
        type: "dataset/queryAllDatasets",
        payload: { pid, force },
      })
    },
    getDataset(id, force) {
      return dispatch({
        type: "dataset/getDataset",
        payload: { id, force },
      })
    },
    clearCache() {
      return dispatch({ type: "dataset/clearCache", })
    },
    mine(payload) {
      return dispatch({
        type: "task/mine",
        payload,
      })
    },
    updateIteration(params) {
      return dispatch({
        type: 'iteration/updateIteration',
        payload: params,
      })
    },
  }
}

export default connect(props, dis)(Mining)
