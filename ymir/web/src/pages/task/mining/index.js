import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Button, Form, Row, Col, ConfigProvider, Space, InputNumber } from "antd"
import styles from "./index.less"
import commonStyles from "../common.less"
import { formLayout } from "@/config/antd"

import t from "@/utils/t"
import { string2Array } from '@/utils/string'
import { TYPES } from '@/constants/image'
import { useHistory, useParams, useLocation } from "umi"
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyStateDataset from '@/components/empty/dataset'
import EmptyStateModel from '@/components/empty/model'
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"
import ModelSelect from "@/components/form/modelSelect"
import ImageSelect from "@/components/form/imageSelect"
import LiveCodeForm from "../components/liveCodeForm"
import { removeLiveCodeConfig } from "../components/liveCodeConfig"
import DockerConfigForm from "../components/dockerConfigForm"
import DatasetSelect from "../../../components/form/datasetSelect"

function Mining({ datasetCache, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { mid, image, iterationId, currentStage, outputKey } = location.query
  const stage = string2Array(mid)
  const did = Number(location.query.did)
  const [dataset, setDataset] = useState({})
  const [selectedModel, setSelectedModel] = useState({})
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [topk, setTopk] = useState(true)
  const [gpu_count, setGPU] = useState(0)
  const [imageHasInference, setImageHasInference] = useState(false)
  const [live, setLiveCode] = useState(false)

  useEffect(() => {
    fetchSysInfo()
  }, [])

  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  useEffect(() => {
    did && func.getDataset(did)
  }, [did])

  useEffect(() => {
    const cache = datasetCache[did]
    if (cache) {
      setDataset(cache)
    }
  }, [datasetCache])

  async function fetchSysInfo() {
    const result = await func.getSysInfo()
    if (result) {
      setGPU(result.gpu_count)
    }
  }

  function filterStrategyChange({ target }) {
    setTopk(target.value)
  }

  function imageChange(_, image = {}) {
    const { url, configs = [] } = image
    const configObj = configs.find(conf => conf.type === TYPES.MINING) || {}
    const hasInference = configs.some(conf => conf.type === TYPES.INFERENCE)
    setImageHasInference(hasInference)
    !hasInference && form.setFieldsValue({ inference: false })
    setLiveCode(image.liveCode || false)
    setConfig(removeLiveCodeConfig(configObj.config))
  }

  function setConfig(config) {
    const params = Object.keys(config).filter(key => key !== 'gpu_count').map(key => ({ key, value: config[key] }))
    setSeniorConfig(params)
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
      topk: values.filter_strategy ? values.topk : 0,
      projectId: pid,
      imageId,
      image,
      config,
    }
    const result = await func.createMiningTask(params)
    if (result) {
      if (iterationId) {
        func.updateIteration({ id: iterationId, currentStage, [outputKey]: result.result_dataset.id })
      }
      await func.clearCache()
      history.replace(`/home/project/${pid}/dataset`)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function setsChange(id, option) {
    setDataset(option?.dataset || {})
  }

  function modelChange(id, options) {
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
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.mining')}>
        <div className={commonStyles.formContainer}>
          <Form
            className={styles.form}
            {...formLayout}
            form={form}
            name='miningForm'
            initialValues={initialValues}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
          >

            <Form.Item name='image' tooltip={t('tip.task.mining.image')} label={t('task.mining.form.image.label')} rules={[
              { required: true, message: t('task.train.form.image.required') }
            ]}>
              <ImageSelect placeholder={t('task.train.form.image.placeholder')}
                relatedId={selectedModel?.task?.parameters?.docker_image_id} type={TYPES.MINING} onChange={imageChange} />
            </Form.Item>

            <ConfigProvider renderEmpty={() => <EmptyStateDataset add={() => history.push(`/home/dataset/add/${pid}`)} />}>

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
            </ConfigProvider>


            <ConfigProvider renderEmpty={() => <EmptyStateModel id={pid} />}>
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
            </ConfigProvider>

            <Form.Item
              tooltip={t('tip.task.filter.strategy')}
              label={t('task.mining.form.strategy.label')}
            >
              <Form.Item
                name='filter_strategy'
                initialValue={true}
                noStyle
              >
                <Form.Item noStyle name='topk' label='topk' dependencies={['filter_strategy']} rules={topk ? [
                  { type: 'number', min: 1, max: (dataset.assetCount - 1) || 1 }
                ] : null}>
                  <InputNumber style={{ width: 120 }} min={1} max={dataset.assetCount - 1} precision={0} />
                </Form.Item>
              </Form.Item>
              <p style={{ display: 'inline-block', marginLeft: 10 }}>{t('task.mining.topk.tip')}</p>
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
              >
                <InputNumber min={0} max={gpu_count} precision={0} /></Form.Item>
              <span style={{ marginLeft: 20 }}>{t('task.gpu.tip', { count: gpu_count })}</span>
            </Form.Item>

            <LiveCodeForm form={form} live={live} />
            <DockerConfigForm form={form} seniorConfig={seniorConfig} />
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.action.mine')}
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
        </div>
      </Card>
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
    createMiningTask(payload) {
      return dispatch({
        type: "task/createMiningTask",
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
