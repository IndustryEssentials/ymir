import React, { useCallback, useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Button, Form, Row, Col, Space, InputNumber, message, Tag, Alert } from "antd"
import { useHistory, useParams, useLocation } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { HIDDENMODULES } from '@/constants/common'
import { string2Array } from "@/utils/string"
import { OPENPAI_MAX_GPU_COUNT } from '@/constants/common'
import { TYPES } from '@/constants/image'
import useFetch from '@/hooks/useFetch'

import Breadcrumbs from "@/components/common/breadcrumb"
import { randomNumber } from "@/utils/number"
import ModelSelect from "@/components/form/modelSelect"
import ImageSelect from "@/components/form/imageSelect"
import DatasetSelect from "@/components/form/datasetSelect"
import useAddKeywords from "@/hooks/useAddKeywords"
import AddKeywordsBtn from "@/components/keyword/addKeywordsBtn"
import LiveCodeForm from "@/components/form/items/liveCode"
import { removeLiveCodeConfig } from "@/components/form/items/liveCodeConfig"
import DockerConfigForm from "@/components/form/items/dockerConfig"
import Desc from "@/components/form/desc"

import commonStyles from "../common.less"
import styles from "./index.less"
import OpenpaiForm from "@/components/form/items/openpai"
import Tip from "@/components/form/tip"

const { Option } = Select

const getArray = (str = '') => str.split('|')
const parseModelStage = (str = '') => {
  return str ? getArray(str).map(stage => string2Array(stage)) : []
}

const Algorithm = () => [{ id: "aldd", label: 'ALDD', checked: true }]

function Inference({ datasetCache, datasets, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { image } = location.query
  const stage = parseModelStage(location.query.mid)
  const [selectedModels, setSelectedModels] = useState([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState({})
  const [gpu_count, setGPU] = useState(0)
  const [taskCount, setTaskCount] = useState(1)
  const [selectedGpu, setSelectedGpu] = useState(0)
  const [keywordRepeatTip, setKRTip] = useState('')
  const [{ newer }, checkKeywords] = useFetch('keyword/checkDuplication', { newer: [] })
  const [live, setLiveCode] = useState(false)
  const [project, getProject] = useFetch('project/getProject', {})
  const watchStages = Form.useWatch('stages', form)
  const watchTestingSets = Form.useWatch('datasets', form)
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
    pid && getProject({ id: pid, force: true })
  }, [pid])

  useEffect(() => {
    const did = location.query?.did ? getArray(location.query.did).map(Number) : undefined

    did && form.setFieldsValue({ datasets: did })
  }, [location.query.did])

  useEffect(() => {

  }, [stage])

  useEffect(() => {
    pid && func.getDatasets(pid)
  }, [pid])

  useEffect(() => {
    checkModelKeywords()
  }, [selectedModels])

  useEffect(() => {
    const taskCount = watchStages?.length * watchTestingSets?.length || 1
    setTaskCount(taskCount)
  }, [watchStages, watchTestingSets])

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
      } = parameters
      form.setFieldsValue({
        datasets: [dataset_id],
        gpu_count: config.gpu_count,
        stages: [[model_id, model_stage_id]],
        image: docker_image_id + ',' + docker_image,
        description,
      })
      setSelectedGpu(config.gpu_count)
      setTimeout(() => setConfig(config), 500)
      setShowConfig(true)

      history.replace({ state: {} })
    }
  }, [location.state])

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
      name: 'task_inference_' + randomNumber(),
      description: (values.description || '').trim(),
      projectId: pid,
      imageId,
      image,
      config,
    }
    const result = await func.infer(params)
    if (result) {
      const tasksCount = values.stages.length * values.datasets.length
      const resultCount = result.filter(item => item).length
      if (resultCount < tasksCount) {
        message.warn(t('task.inference.failure.some'))
      }
      await func.clearCache()
      const groups = result.map(item => item.result_dataset?.dataset_group_id || '')
      console.log('groups:', groups, resultCount, taskCount, result)
      history.replace(`/home/project/${pid}/dataset#${groups.join(',')}`)
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
          >
            <Form.Item wrapperCol={{ span: 20 }}><Tip content={t('task.inference.header.tip')} /></Form.Item>
            <Form.Item
              label={t('task.inference.form.dataset.label')}
              required
              name="datasets"
              rules={[
                { required: true, message: t('task.inference.form.dataset.required') },
              ]}
            >
              <DatasetSelect
                mode='multiple'
                pid={pid}
                filters={testSetFilters}
                renderLabel={renderLabel}
                placeholder={t('task.inference.form.dataset.placeholder')}
              />
            </Form.Item>
            <Form.Item required
              tooltip={t('tip.task.filter.imodel')}
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
              <div style={{ marginTop: 10 }}>
                <Button size='small' type="primary" onClick={() => selectModelFromIteration()}>
                  {t('task.inference.model.iters')}
                </Button>
              </div>
            </Form.Item>

            <Form.Item name='image' tooltip={t('tip.task.inference.image')} label={t('task.inference.form.image.label')} rules={[
              { required: true, message: t('task.inference.form.image.required') }
            ]}>
              <ImageSelect
                placeholder={t('task.inference.form.image.placeholder')}
                relatedId={selectedModels[0]?.task?.parameters?.docker_image_id}
                type={TYPES.INFERENCE}
                onChange={imageChange}
              />
            </Form.Item>
            <OpenpaiForm form={form} openpai={openpai} />
            <Form.Item
              tooltip={t('tip.task.filter.igpucount')}
              label={t('task.gpu.count')}
            >
              <Form.Item
                noStyle
                name="gpu_count"
                rules={[
                  {
                    validator: (rules, value) => value <= Math.floor(gpu_count / taskCount) ?
                      Promise.resolve() :
                      Promise.reject(),
                    message: t('task.infer.gpu.tip', { total: gpu_count, selected: taskCount * selectedGpu })
                  }
                ]}
              >
                <InputNumber min={0} max={Math.floor(gpu_count / taskCount)} precision={0} onChange={setSelectedGpu} />
              </Form.Item>
              <span style={{ marginLeft: 20 }}>
                {t('task.infer.gpu.tip', { total: gpu_count, selected: taskCount * selectedGpu })}
              </span>
            </Form.Item>

            <LiveCodeForm form={form} live={live} />
            <DockerConfigForm form={form} show={showConfig} seniorConfig={seniorConfig} />

            <Desc form={form} />

            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit" >
                    {t('common.action.inference')}
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
    infer(payload) {
      return dispatch({
        type: "task/infer",
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
