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

const { Option } = Select

const Algorithm = () => [{ id: "aldd", label: 'ALDD', checked: true }]

function Inference({ datasetCache, datasets, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { did, image } = location.query
  const mid = string2Array(location.query.mid) || []
  const [dataset, setDataset] = useState({})
  const [selectedModels, setSelectedModels] = useState([])
  const [gpuStep, setGpuStep] = useState(1)
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [hpVisible, setHpVisible] = useState(false)
  const [gpu_count, setGPU] = useState(0)
  const [selectedGpu, setSelectedGpu] = useState(0)
  const [keywordRepeatTip, setKRTip] = useState('')
  const [{ newer }, checkKeywords] = useAddKeywords(true)

  useEffect(() => {
    fetchSysInfo()
  }, [])

  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  useEffect(() => {
    did && func.getDataset(did)
    did && form.setFieldsValue({ datasetId: Number(did) })
  }, [did])

  useEffect(() => {
    mid?.length && form.setFieldsValue({ model: mid })
  }, [location.query.mid])

  useEffect(() => {
    datasetCache[did] && setDataset(datasetCache[did])
  }, [datasetCache])

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

  function validHyperparam(rule, value) {

    const params = form.getFieldValue('hyperparam').map(({ key }) => key)
      .filter(item => item && item.trim() && item === value)
    if (params.length > 1) {
      return Promise.reject(t('task.validator.same.param'))
    } else {
      return Promise.resolve()
    }
  }

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
    setConfig(configObj.config)
  }

  function setConfig(config) {
    const params = Object.keys(config).filter(key => key !== 'gpu_count').map(key => ({ key, value: config[key] }))
    setSeniorConfig(params)
  }

  const onFinish = async (values) => {
    const config = {}
    form.getFieldValue('hyperparam').forEach(({ key, value }) => key && value ? config[key] = value : null)

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
      if (result.filter(item => item).length !== values.model.length) {
        message.warn(t('task.inference.failure.some'))
      }
      await func.clearCache()
      history.replace(`/home/project/detail/${pid}`)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function setsChange(id) {
    id && setDataset(datasets.find(ds => ds.id === id))
  }

  function modelChange(id, options = []) {
    setSelectedModels(options.map(({ model }) => model) || [])
  }

  async function selectModelFromIteration() {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      const models = iterations.map(iter => iter.model) || []
      form.setFieldsValue({ model: models })
    }
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    description: '',
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
                  name="datasetId"
                  rules={[
                    { required: true, message: t('task.inference.form.dataset.required') },
                  ]}
                >
                  <DatasetSelect pid={pid} placeholder={t('task.inference.form.dataset.placeholder')} onChange={setsChange} showArrow />
                </Form.Item>
              </Tip>
            </ConfigProvider>


            <ConfigProvider renderEmpty={() => <EmptyStateModel id={pid} />}>
              <Tip content={t('tip.task.filter.imodel')}>
                <Form.Item required
                  label={t('task.mining.form.model.label')}>
                  <Form.Item
                    noStyle
                    name="model"
                    rules={[
                      { required: true, message: t('task.mining.form.model.required') },
                    ]}
                  >
                    <ModelSelect mode='multiple' placeholder={t('task.inference.form.model.required')} onChange={modelChange} pid={pid} />
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

            {seniorConfig.length ? <Tip content={t('tip.task.filter.ihyperparams')}>
              <Form.Item
                label={t('task.train.form.hyperparam.label')}
                rules={[{ validator: validHyperparam }]}
              >
                <div>
                  <Button type='link'
                    onClick={() => setHpVisible(!hpVisible)}
                    icon={hpVisible ? <UpSquareOutlined /> : <DownSquareOutlined />}
                    style={{ paddingLeft: 0 }}
                  >{hpVisible ? t('task.train.fold') : t('task.train.unfold')}
                  </Button>
                </div>

                <Form.List name='hyperparam'>
                  {(fields, { add, remove }) => (
                    <div className={styles.paramContainer} hidden={!hpVisible}>
                      <Row style={{ backgroundColor: '#fafafa', lineHeight: '40px', marginBottom: 10 }} gutter={20}>
                        <Col flex={'240px'}>{t('common.key')}</Col>
                        <Col flex={1}>{t('common.value')}</Col>
                        <Col span={2}>{t('common.action')}</Col>
                      </Row>
                      {fields.map(field => (
                        <Row key={field.key} gutter={20}>
                          <Col flex={'240px'}>
                            <Form.Item
                              {...field}
                              // label="Key"
                              name={[field.name, 'key']}
                              fieldKey={[field.fieldKey, 'key']}
                              rules={[
                                // {required: true, message: 'Missing Key'},
                                { validator: validHyperparam }
                              ]}
                            >
                              <Input disabled={field.key < seniorConfig.length} allowClear maxLength={50} />
                            </Form.Item>
                          </Col>
                          <Col flex={1}>
                            <Form.Item
                              {...field}
                              // label="Value"
                              name={[field.name, 'value']}
                              fieldKey={[field.fieldKey, 'value']}
                              rules={[
                                // {required: true, message: 'Missing Value'},
                              ]}
                            >
                              {seniorConfig[field.name] && typeof seniorConfig[field.name].value === 'number' ?
                                <InputNumber style={{ minWidth: '100%' }} maxLength={20} /> : <Input allowClear maxLength={100} />}
                            </Form.Item>
                          </Col>
                          <Col span={2}>
                            <Space>
                              {field.name < seniorConfig.length ? null : <MinusCircleOutlined onClick={() => remove(field.name)} />}
                              {field.name === fields.length - 1 ? <PlusOutlined onClick={() => add()} title={t('task.train.parameter.add.label')} /> : null}
                            </Space>
                          </Col>
                        </Row>
                      ))}

                    </div>
                  )}
                </Form.List>

              </Form.Item>
            </Tip> : null}

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
