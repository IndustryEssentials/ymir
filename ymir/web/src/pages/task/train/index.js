import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Button, Form, Row, Col, ConfigProvider, Space, InputNumber, Tag } from "antd"
import {
  PlusOutlined,
  MinusCircleOutlined,
  UpSquareOutlined,
  DownSquareOutlined,
} from '@ant-design/icons'
import { formLayout } from "@/config/antd"
import { useHistory, useParams, useLocation } from "umi"

import t from "@/utils/t"
import { TYPES } from '@/constants/image'
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyState from '@/components/empty/dataset'
import EmptyStateModel from '@/components/empty/model'
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"
import ImageSelect from "@/components/form/imageSelect"
import styles from "./index.less"
import commonStyles from "../common.less"
import ModelSelect from "@/components/form/modelSelect"
import KeywordRates from "@/components/dataset/keywordRates"

const { Option } = Select

const TrainType = () => [{ id: "detection", label: t('task.train.form.traintypes.detect'), checked: true }]
const FrameworkType = () => [{ id: "YOLO v4", label: "YOLO v4", checked: true }]
const Backbone = () => [{ id: "darknet", label: "Darknet", checked: true }]

function Train({ allDatasets, datasetCache, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { did, mid, image, iterationId, outputKey, currentStage, test } = location.query
  const [datasets, setDatasets] = useState([])
  const [dataset, setDataset] = useState({})
  const [trainSet, setTrainSet] = useState(null)
  const [testSet, setTestSet] = useState(null)
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [hpVisible, setHpVisible] = useState(false)
  const [gpu_count, setGPU] = useState(0)

  const renderRadio = (types) => {
    return (
      <Radio.Group>
        {types.map((type) => (
          <Radio value={type.id} key={type.id} defaultChecked={type.checked}>
            {type.label}
          </Radio>
        ))}
      </Radio.Group>
    )
  }

  useEffect(() => {
    fetchSysInfo()
  }, [])

  useEffect(() => {
    setDatasets(allDatasets)
  }, [allDatasets])

  useEffect(() => {
    if (did) {
      func.getDataset(did)
      setTrainSet(did)
    }
  }, [did])

  useEffect(() => {
    const dst = datasetCache[did]
    dst && setDataset(dst)
  }, [datasetCache])

  useEffect(() => {
    pid && func.getDatasets(pid)
  }, [pid])

  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  useEffect(() => {
    const state = location.state

    if (state?.record) {
      const { parameters, name, config, } = state.record
      const { validation_dataset_id, strategy, docker_image, docker_image_id, model_id } = parameters
      form.setFieldsValue({
        testset: validation_dataset_id,
        gpu_count: config.gpu_count,
        model: model_id,
        image: docker_image_id + ',' + docker_image,
        strategy,
      })
      setConfig(config)
      setTestSet(validation_dataset_id)
      setHpVisible(true)

      history.replace({ state: {} })
    }
  }, [location.state])

  async function validHyperparam(rule, value) {

    const params = form.getFieldValue('hyperparam').map(({ key }) => key)
      .filter(item => item && item.trim() && item === value)
    if (params.length > 1) {
      return Promise.reject(t('task.validator.same.param'))
    } else {
      return Promise.resolve()
    }
  }

  async function fetchSysInfo() {
    const result = await func.getSysInfo()
    if (result) {
      setGPU(result.gpu_count)
    }
  }

  function trainSetChange(value) {
    setTrainSet(value)
  }
  function validationSetChange(value) {
    setTestSet(value)
  }

  function modelChange(value, model) {
    setSelectedModel(model)
  }

  function imageChange(_, image = {}) {
    const { configs } = image
    const configObj = (configs || []).find(conf => conf.type === TYPES.TRAINING) || {}
    setConfig(configObj.config)
  }

  function setConfig(config = {}) {
    const params = Object.keys(config).filter(key => key !== 'gpu_count').map(key => ({ key, value: config[key] }))
    setSeniorConfig(params)
  }

  const onFinish = async (values) => {
    const config = {}
    form.getFieldValue('hyperparam').forEach(({ key, value }) => key && value ? config[key] = value : null)

    const gpuCount = form.getFieldValue('gpu_count')
    if (gpuCount) {
      config['gpu_count'] = gpuCount
    }
    const img = (form.getFieldValue('image') || '').split(',')
    const imageId = Number(img[0])
    const image = img[1]
    const params = {
      ...values,
      name: 'group_' + randomNumber(),
      projectId: pid,
      keywords: dataset.project.keywords,
      image,
      imageId,
      config,
    }
    const result = await func.createTrainTask(params)
    if (result) {
      if (iterationId) {
        func.updateIteration({ id: iterationId, currentStage, [outputKey]: result.result_model.id })
      }
      await func.clearCache()
      history.replace(`/home/project/detail/${pid}#model`)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function getTrainSetTotal(setId) {
    const ds = datasets.find(d => d.id === setId)
    return ds ? ds.assetCount : 0
  }

  function validateGPU(_, value) {
    const count = Number(value)
    const min = 1
    const max = gpu_count
    if (count < min || count > max) {
      return Promise.reject(t('task.train.gpu.invalid', { min, max }))
    }
    return Promise.resolve()
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_train_' + randomNumber(),
    datasetId: Number(did) ? Number(did) : undefined,
    testset: Number(test) ? Number(test) : undefined,
    image: image ? parseInt(image) : undefined,
    model: mid ? parseInt(mid) : undefined,
    trainType: getCheckedValue(TrainType()),
    network: getCheckedValue(FrameworkType()),
    backbone: getCheckedValue(Backbone()),
    gpu_count: 1,
  }
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.training')}>
        <div className={commonStyles.formContainer}>
          <Form
            name='trainForm'
            className={styles.form}
            {...formLayout}
            form={form}
            initialValues={initialValues}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            labelAlign={'left'}
            colon={false}
            scrollToFirstError
          >
            <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push(`/home/dataset/add/${pid}`)} />}>
              <Tip hidden={true}>
                <Form.Item
                  label={t('task.train.form.trainsets.label')}
                  required
                  name="datasetId"
                  rules={[
                    { required: true, message: t('task.train.form.datasets.required') },
                  ]}
                >
                  <Select
                    placeholder={t('task.train.form.training.datasets.placeholder')}
                    filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    onChange={trainSetChange}
                    disabled={did}
                    showArrow
                  >
                    {datasets.filter(ds => ds.id !== testSet).map(item =>
                      <Option value={item.id} key={item.name}>
                        {item.name} {item.versionName}(assets: {item.assetCount})
                      </Option>
                    )}
                  </Select>
                </Form.Item>
              </Tip>
              <Tip content={t('tip.task.filter.testsets')}>
                <Form.Item
                  label={t('task.train.form.testsets.label')}
                  name="testset"
                  rules={[
                    { required: true, message: t('task.train.form.datasets.required') },
                  ]}
                >
                  <Select
                    disabled={test}
                    placeholder={t('task.train.form.test.datasets.placeholder')}
                    filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    onChange={validationSetChange}
                    showArrow
                  >
                    {datasets.filter(ds => ds.id !== trainSet).map(item =>
                      <Option value={item.id} key={item.name}>
                        {item.name}({item.assetCount})
                      </Option>
                    )}
                  </Select>
                </Form.Item>
              </Tip>
            </ConfigProvider>
            <Tip hidden={true}>
              <Form.Item label={t('dataset.train.form.samples')}>
                <KeywordRates id={trainSet} trainingKeywords={dataset?.project?.keywords} total={getTrainSetTotal(trainSet)}></KeywordRates>
              </Form.Item>
            </Tip>
            <Tip content={t('tip.task.filter.keywords')}>
              <Form.Item label={t('task.train.form.keywords.label')}>
                {dataset?.project?.keywords.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}
              </Form.Item>
            </Tip>
            <ConfigProvider renderEmpty={() => <EmptyStateModel id={pid} />}>
              <Tip content={t('tip.task.train.model')}>
                <Form.Item
                  label={t('task.mining.form.model.label')}
                  name="model"
                >
                  <ModelSelect placeholder={t('task.train.form.model.placeholder')} pid={pid} />
                </Form.Item>
              </Tip>
            </ConfigProvider>

            <Tip content={t('tip.task.train.image')}>
              <Form.Item name='image' label={t('task.train.form.image.label')} rules={[
                { required: true, message: t('task.train.form.image.required') }
              ]}>
                <ImageSelect placeholder={t('task.train.form.image.placeholder')} onChange={imageChange} />
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item
                label={t('task.train.form.traintype.label')}
                name="trainType"
              >
                {renderRadio(TrainType())}
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item
                label={t('task.train.form.network.label')}
                name="network"
              >
                {renderRadio(FrameworkType())}
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item
                label={t('task.train.form.backbone.label')}
                name="backbone"
              >
                {renderRadio(Backbone())}
              </Form.Item>
            </Tip>

            <Tip content={t('tip.task.filter.gpucount')}>
              <Form.Item
                label={t('task.gpu.count')}
              >
                <Form.Item
                  noStyle
                  name="gpu_count"
                  rules={[
                    { validator: validateGPU }
                  ]}
                >
                  <InputNumber min={1} max={gpu_count} precision={0} /></Form.Item>
                <span style={{ marginLeft: 20 }}>{t('task.gpu.tip', { count: gpu_count })}</span>
              </Form.Item>
            </Tip>

            {seniorConfig.length ? <Tip content={t('tip.task.filter.hyperparams')}>
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
                    <>
                      <div className={styles.paramContainer} hidden={!hpVisible}>
                        <Row style={{ backgroundColor: '#fafafa', border: '1px solid #f4f4f4', lineHeight: '40px', marginBottom: 10 }} gutter={20}>
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
                                <Input disabled={field.name < seniorConfig.length} allowClear maxLength={50} />
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
                                  <InputNumber maxLength={20} style={{ minWidth: '100%' }} /> : <Input allowClear maxLength={100} />}
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
                    </>
                  )}
                </Form.List>

              </Form.Item>
            </Tip> : null}
            <Tip hidden={true}>
              <Form.Item wrapperCol={{ offset: 8 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit" disabled={!gpu_count}>
                      {t('task.create')}
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
    allDatasets: state.dataset.allDatasets,
    datasetCache: state.dataset.dataset,
  }
}

const dis = (dispatch) => {
  return {
    getDatasets(pid, force) {
      return dispatch({
        type: "dataset/queryAllDatasets",
        payload: { pid, force },
      })
    },
    getDataset(id) {
      return dispatch({
        type: "dataset/getDataset",
        payload: id,
      })
    },
    clearCache() {
      return dispatch({ type: "model/clearCache", })
    },
    getSysInfo() {
      return dispatch({
        type: "common/getSysInfo",
      })
    },
    createTrainTask(payload) {
      return dispatch({
        type: "task/createTrainTask",
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

export default connect(props, dis)(Train)
