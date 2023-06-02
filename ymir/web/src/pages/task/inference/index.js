import React, { useCallback, useEffect, useState } from 'react'
import { connect } from 'dva'
import { Select, Card, Button, Form, Row, Col, Space, InputNumber, message, Tag, Alert } from 'antd'
import { useHistory, useParams, useLocation } from 'umi'

import { formLayout } from '@/config/antd'
import t from '@/utils/t'
import { HIDDENMODULES } from '@/constants/common'
import { string2Array } from '@/utils/string'
import { OPENPAI_MAX_GPU_COUNT } from '@/constants/common'
import { TYPES, getConfig } from '@/constants/image'
import { isMultiModal } from '@/constants/objectType'
import useFetch from '@/hooks/useFetch'
import useRequest from '@/hooks/useRequest'

import Breadcrumbs from '@/components/common/breadcrumb'
import { randomNumber } from '@/utils/number'
import ModelSelect from '@/components/form/modelSelect'
import ImageSelect from '@/components/form/ImageSelect'
import DatasetSelect from '@/components/form/datasetSelect'
import AddKeywordsBtn from '@/components/keyword/addKeywordsBtn'
import LiveCodeForm from '@/components/form/items/liveCode'
import { removeLiveCodeConfig } from '@/components/form/items/liveCodeConfig'
import DockerConfigForm from '@/components/form/items/DockerConfig'
import Desc from '@/components/form/desc'
import Dataset from '@/components/form/option/Dataset'
import ObjectTypeSelector, { Types } from '@/components/form/InferObjectTypeSelector'

import commonStyles from '../common.less'
import styles from './index.less'
import OpenpaiForm from '@/components/form/items/openpai'
import Tip from '@/components/form/tip'

function Inference({ ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { image } = location.query
  const stage = string2Array(location.query.mid)
  const [selectedModel, setSelectedModel] = useState(null)
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState({})
  const [gpu_count, setGPU] = useState(0)
  const [keywordRepeatTip, setKRTip] = useState('')
  const [{ newer }, checkKeywords] = useFetch('keyword/checkDuplication', { newer: [] })
  const [live, setLiveCode] = useState(false)
  const [liveInitialValues, setLiveInitialValues] = useState({})
  const [project, getProject] = useFetch('project/getProject', {})
  const [openpai, setOpenpai] = useState(false)
  const [sys, getSysInfo] = useFetch('common/getSysInfo', {})
  const selectOpenpai = Form.useWatch('openpai', form)
  const [showConfig, setShowConfig] = useState(false)
  const { runAsync: getAllKeywords } = useRequest('keyword/getAllKeywords', { loading: false })

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
    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    const did = Number(location.query?.did)

    did && form.setFieldsValue({ dataset: did })
  }, [location.query.did])

  useEffect(() => {
    checkModelKeywords()
  }, [selectedModel])

  useEffect(() => {
    if (newer.length) {
      const tip = (
        <>
          {t('task.inference.unmatch.keywrods', {
            keywords: newer.map((key) => <Tag key={key}>{key}</Tag>),
          })}
          <AddKeywordsBtn type="primary" size="small" style={{ marginLeft: 10 }} keywords={newer} callback={checkModelKeywords} />
        </>
      )
      setKRTip(tip)
    }
  }, [newer])

  useEffect(() => {
    const state = location.state

    if (state?.record) {
      const {
        task: { parameters, config },
        description,
      } = state.record
      const { dataset_id, docker_image_id, model_id, model_stage_id } = parameters
      form.setFieldsValue({
        dataset: dataset_id,
        gpu_count: config.gpu_count,
        stages: [[model_id, model_stage_id]],
        image: docker_image_id,
        description,
      })
      if (!HIDDENMODULES.LIVECODE) {
        setLiveCode(!!config.git_url)
        setLiveInitialValues(config)
      }
      setTimeout(() => setConfig(removeLiveCodeConfig(config)), 500)
      setShowConfig(true)

      history.replace({ state: {} })
    }
  }, [location.state])

  function checkModelKeywords() {
    selectedModel?.keywords.length && checkKeywords(selectedModel?.keywords)
  }

  function imageChange(_, option) {
    if (!option) {
      return setConfig({})
    }
    const { image, objectType } = option
    const configObj = getConfig(option.image, TYPES.INFERENCE, objectType) || {}
    if (!HIDDENMODULES.LIVECODE) {
      setLiveCode(image.liveCode || false)
    }
    setConfig(removeLiveCodeConfig(configObj.config))
  }

  function setConfig(config = {}) {
    setSeniorConfig(config)
  }

  const onFinish = async (values) => {
    const prompt = values.objectType === Types.All ? (await getAllKeywords())?.map((kw) => kw.name) : selectedModel.keywords
    const config = {
      ...values.hyperparam?.reduce((prev, { key, value }) => (key && value ? { ...prev, [key]: value } : prev), {}),
      ...(values.live || {}),
      prompt: prompt.join(';'),
    }

    config['gpu_count'] = form.getFieldValue('gpu_count') || 0

    const params = {
      ...values,
      name: 'task_inference_' + randomNumber(),
      description: (values.description || '').trim(),
      projectId: pid,
      config,
    }
    const result = await func.infer(params)
    if (result) {
      history.replace(`/home/project/${pid}/prediction`)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log('Failed:', errorInfo)
  }

  function modelChange(id, option = []) {
    const opt = option[0]
    const model = opt?.model
    setSelectedModel(model)
  }

  async function selectModelFromIteration() {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      const models = iterations.map((iter) => (iter.model ? [iter.model] : null)).filter((i) => i) || []
      form.setFieldsValue({ stage: models })
    }
  }

  const testSetFilters = useCallback(
    (datasets) => {
      const testings = datasets.filter((ds) => project.testingSets?.includes(ds.id)).map((ds) => ({ ...ds, isProjectTesting: true }))
      const others = datasets.filter((ds) => !project.testingSets?.includes(ds.id))
      return [...testings, ...others]
    },
    [project.testingSets],
  )

  const renderLabel = (item) => (
    <Row>
      <Col flex={1}>
        <Dataset dataset={item} />
      </Col>
      <Col>{item.isProjectTesting ? t('project.testing.dataset.label') : null}</Col>
    </Row>
  )

  const initialValues = {
    description: '',
    stage,
    image: image ? parseInt(image) : undefined,
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
            name="inferenceForm"
            initialValues={initialValues}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
          >
            <Form.Item wrapperCol={{ span: 20 }}>
              <Tip content={t('task.inference.header.tip')} />
            </Form.Item>
            <Form.Item
              label={t('task.inference.form.dataset.label')}
              required
              name="dataset"
              rules={[{ required: true, message: t('task.inference.form.dataset.required') }]}
            >
              <DatasetSelect pid={pid} filters={testSetFilters} renderLabel={renderLabel} placeholder={t('task.inference.form.dataset.placeholder')} />
            </Form.Item>
            <Form.Item required tooltip={t('tip.task.filter.imodel')} label={t('task.mining.form.model.label')}>
              <Form.Item noStyle name="stage" rules={[{ required: true, message: t('task.mining.form.model.required') }]}>
                <ModelSelect placeholder={t('task.inference.form.model.required')} onChange={modelChange} pid={pid} />
              </Form.Item>
              {project.enableIteration ? (
                <div style={{ marginTop: 10 }}>
                  <Button size="small" type="primary" onClick={() => selectModelFromIteration()}>
                    {t('task.inference.model.iters')}
                  </Button>
                </div>
              ) : null}
            </Form.Item>

            <Form.Item
              name="image"
              tooltip={t('tip.task.inference.image')}
              label={t('task.inference.form.image.label')}
              rules={[{ required: true, message: t('task.inference.form.image.required') }]}
            >
              <ImageSelect
                placeholder={t('task.inference.form.image.placeholder')}
                pid={pid}
                relatedId={selectedModel?.task?.parameters?.docker_image_id}
                type={TYPES.INFERENCE}
                onChange={imageChange}
              />
            </Form.Item>
            {isMultiModal(project.type) ? <ObjectTypeSelector /> : null}
            <OpenpaiForm form={form} openpai={openpai} />
            <Form.Item tooltip={t('tip.task.filter.igpucount')} label={t('task.gpu.count')}>
              <Form.Item
                noStyle
                name="gpu_count"
                rules={[
                  {
                    validator: (rules, value) => (value <= gpu_count ? Promise.resolve() : Promise.reject()),
                    message: t('task.gpu.tip', { count: gpu_count }),
                  },
                ]}
              >
                <InputNumber min={0} max={gpu_count} precision={0} />
              </Form.Item>
              <span style={{ marginLeft: 20 }}>{t('task.gpu.tip', { count: gpu_count })}</span>
            </Form.Item>

            <LiveCodeForm form={form} live={live} initialValues={liveInitialValues} />
            <DockerConfigForm form={form} show={showConfig} seniorConfig={seniorConfig} />

            <Desc form={form} />

            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name="submitBtn" noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.action.inference')}
                  </Button>
                </Form.Item>
                <Form.Item name="backBtn" noStyle>
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

const dis = (dispatch) => {
  return {
    infer(payload) {
      return dispatch({
        type: 'task/infer',
        payload,
      })
    },
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id },
      })
    },
  }
}

export default connect(null, dis)(Inference)
