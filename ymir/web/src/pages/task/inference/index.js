import React, { useCallback, useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Button, Form, Row, Col, ConfigProvider, Space, InputNumber, message, Tag, Alert } from "antd"
import {
  PlusOutlined,
  MinusCircleOutlined,
  UpSquareOutlined,
  DownSquareOutlined,
} from '@ant-design/icons'
import styles from "./index.less"
import commonStyles from "../common.less"
import { formLayout } from "@/config/antd"

import t from "@/utils/t"
import { string2Array } from "@/utils/string"
import { TYPES } from '@/constants/image'
import { useHistory, useParams, useLocation } from "umi"
import useFetch from '@/hooks/useFetch'
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyStateDataset from '@/components/empty/dataset'
import EmptyStateModel from '@/components/empty/model'
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"
import ModelSelect from "@/components/form/modelSelect"
import ImageSelect from "@/components/form/imageSelect"
import DatasetSelect from "@/components/form/datasetSelect"
import useAddKeywords from "@/hooks/useAddKeywords"
import AddKeywordsBtn from "@/components/keyword/addKeywordsBtn"
import LiveCodeForm from "../components/liveCodeForm"
import { removeLiveCodeConfig } from "../components/liveCodeConfig"
import DockerConfigForm from "../components/dockerConfigForm"

const { Option } = Select

const parseModelStage = (str = '') => {
  return str ? str.split('|').map(stage => string2Array(stage)) : []
}

const Algorithm = () => [{ id: "aldd", label: 'ALDD', checked: true }]

function Inference({ datasetCache, datasets, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { did, image } = location.query
  const stage = parseModelStage(location.query.mid)
  const [selectedModels, setSelectedModels] = useState([])
  const [gpuStep, setGpuStep] = useState(1)
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [gpu_count, setGPU] = useState(0)
  const [selectedGpu, setSelectedGpu] = useState(0)
  const [keywordRepeatTip, setKRTip] = useState('')
  const [{ newer }, checkKeywords] = useAddKeywords(true)
  const [live, setLiveCode] = useState(false)
  const [project, getProject] = useFetch('project/getProject', {})

  useEffect(() => {
    fetchSysInfo()
  }, [])

  useEffect(() => {
    pid && getProject({ id: pid, force: true })
  }, [pid])

  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  useEffect(() => {
    did && form.setFieldsValue({ datasets: [Number(did)] })
  }, [did])

  useEffect(() => {

  }, [stage])

  useEffect(() => {
    pid && func.getDatasets(pid)
  }, [pid])

  useEffect(() => {
    setGpuStep(selectedModels.length || 1)

    checkModelKeywords()
  }, [selectedModels])

  useEffect(() => {
    if (newer.length) {
      const tip = <>
        {t('task.inference.unmatch.keywrods', {
          keywords: newer.map(key => <Tag key={key}>{key}</Tag>)
        })}
        <AddKeywordsBtn type="primary" size="small" style={{ marginLeft: 10 }} keywords={newer} callback={checkModelKeywords} />
      </>
      setKRTip(tip)
    }
  }, [newer])

  function checkModelKeywords() {
    const keywords = (selectedModels.map(model => model?.keywords) || []).flat().filter(item => item)
    checkKeywords(keywords)
  }

  async function fetchSysInfo() {
    const result = await func.getSysInfo()
    if (result) {
      setGPU(result.gpu_count)
    }
  }

  function imageChange(_, image = {}) {
    const { url, configs = [] } = image
    const configObj = configs.find(conf => conf.type === TYPES.INFERENCE) || {}
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
      name: 'task_inference_' + randomNumber(),
      description: (values.description || '').trim(),
      projectId: pid,
      imageId,
      image,
      config,
    }
    const result = await func.createInferenceTask(params)
    if (result) {
      const tasksCount = values.stages.length * values.datasets.length
      const resultCount = result.filter(item => item).length
      if (resultCount < tasksCount) {
        message.warn(t('task.inference.failure.some'))
      }
      await func.clearCache()
      history.replace(`/home/project/${pid}/dataset`)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function modelChange(id, options = []) {
    const models = options.map(([{ model }]) => model) || []
    setSelectedModels(models)
  }

  async function selectModelFromIteration() {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      const models = iterations.map(iter => iter.model) || []
      form.setFieldsValue({ model: models })
    }
  }

  const testSetFilters = useCallback(datasets => {
    const testings = datasets.filter(ds => project.testingSets?.includes(ds.id)).map(ds => ({ ...ds, isProjectTesting: true }))
    const others = datasets.filter(ds => !project.testingSets?.includes(ds.id))
    return [...testings, ...others]
  }, [project.testingSets])

  const renderLabel = item => <Row>
    <Col flex={1}>{item.name} {item.versionName}(assets: {item.assetCount})</Col>
    <Col>{item.isProjectTesting ? t('project.testing.dataset.label') : null}</Col>
  </Row>

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    description: '',
    stages: stage.length ? stage : undefined,
    image: image ? parseInt(image) : undefined,
    algorithm: getCheckedValue(Algorithm()),
    gpu_count: 0,
  }
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.inference')}>
        {keywordRepeatTip ? <Alert style={{ marginBottom: 20 }} message={keywordRepeatTip} type="warning" showIcon closable /> : null}
        <div className={commonStyles.formContainer}>
          <Form
            className={styles.form}
            {...formLayout}
            form={form}
            name='inferenceForm'
            initialValues={initialValues}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            labelAlign={'left'}
            colon={false}
            scrollToFirstError
          >
            <ConfigProvider renderEmpty={() => <EmptyStateDataset add={() => history.push(`/home/dataset/add/${pid}`)} />}>

              <Tip hidden={true}>
                <Form.Item
                  label={t('task.inference.form.dataset.label')}
                  required
                  name="datasets"
                  rules={[
                    { required: true, message: t('task.inference.form.dataset.required') },
                  ]}
                >
                  <DatasetSelect mode='multiple' pid={pid} filters={testSetFilters} renderLabel={renderLabel} placeholder={t('task.inference.form.dataset.placeholder')} />
                </Form.Item>
              </Tip>
            </ConfigProvider>


            <ConfigProvider renderEmpty={() => <EmptyStateModel id={pid} />}>
              <Tip content={t('tip.task.filter.imodel')}>
                <Form.Item required
                  label={t('task.mining.form.model.label')}>
                  <Form.Item
                    noStyle
                    name="stages"
                    rules={[
                      { required: true, message: t('task.mining.form.model.required') },
                    ]}
                  >
                    <ModelSelect multiple placeholder={t('task.inference.form.model.required')} onChange={modelChange} pid={pid} />
                  </Form.Item>
                  <div style={{ marginTop: 10 }}><Button size='small' type="primary" onClick={() => selectModelFromIteration()}>{t('task.inference.model.iters')}</Button></div>
                </Form.Item>
              </Tip>
            </ConfigProvider>

            <Tip content={t('tip.task.inference.image')}>
              <Form.Item name='image' label={t('task.train.form.image.label')} rules={[
                { required: true, message: t('task.inference.form.image.required') }
              ]}>
                <ImageSelect placeholder={t('task.inference.form.image.placeholder')} relatedId={selectedModels[0]?.task?.parameters?.docker_image_id} type={TYPES.INFERENCE} onChange={imageChange} />
              </Form.Item>
            </Tip>

            <Tip content={t('tip.task.filter.igpucount')}>
              <Form.Item
                label={t('task.gpu.count')}
              >
                <Form.Item
                  noStyle
                  name="gpu_count"
                >
                  <InputNumber min={0} max={Math.floor(gpu_count / gpuStep)} precision={0} onChange={setSelectedGpu} /></Form.Item>
                <span style={{ marginLeft: 20 }}>
                  {t('task.infer.gpu.tip', { total: gpu_count, selected: gpuStep * selectedGpu })}
                </span>
              </Form.Item>
            </Tip>

            <LiveCodeForm live={live} />
            <DockerConfigForm form={form} seniorConfig={seniorConfig} />

            <Tip hidden={true}>
              <Form.Item label={t('task.inference.form.desc')} name='description'
                rules={[
                  { max: 500 },
                ]}
              >
                <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item wrapperCol={{ offset: 8 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit" >
                      {t('common.action.infer')}
                    </Button>
                  </Form.Item>
                  <Form.Item name='backBtn' noStyle>
                    <Button size="large" onClick={() => history.goBack()}>
                      {t('task.btn.back')}
                    </Button>
                  </Form.Item>
                </Space>
              </Form.Item>
            </Tip>
          </Form>
        </div>
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    datasets: state.dataset.allDatasets,
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
    getDatasets(pid) {
      return dispatch({
        type: "dataset/queryAllDatasets",
        payload: { pid, force: true },
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
    createInferenceTask(payload) {
      return dispatch({
        type: "task/createInferenceTask",
        payload,
      })
    },
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id, more: true },
      })
    },
  }
}

export default connect(props, dis)(Inference)
