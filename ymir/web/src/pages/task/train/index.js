import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Button, Form, Row, Col, ConfigProvider, Space, InputNumber, Tag, message } from "antd"
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
import CheckProjectDirty from "@/components/common/CheckProjectDirty"

const { Option } = Select

const TrainType = () => [{ id: "detection", label: t('task.train.form.traintypes.detect'), checked: true }]
const FrameworkType = () => [{ id: "YOLO v4", label: "YOLO v4", checked: true }]
const Backbone = () => [{ id: "darknet", label: "Darknet", checked: true }]

function Train({ allDatasets, datasetCache, keywords, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { mid, image, iterationId, outputKey, currentStage, test } = location.query
  const did = Number(location.query.did)
  const [project, setProject] = useState({})
  const [datasets, setDatasets] = useState([])
  const [dataset, setDataset] = useState({})
  const [trainSet, setTrainSet] = useState(null)
  const [testSet, setTestSet] = useState(null)
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [hpVisible, setHpVisible] = useState(false)
  const [gpu_count, setGPU] = useState(0)
  const [projectDirty, setProjectDirty] = useState(false)

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
    fetchProject()
  }, [])

  useEffect(() => {
    func.getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    const dss = allDatasets.filter(ds => ds.keywords.some(kw => project?.keywords?.includes(kw)))
    setDatasets(dss)
    const isValid = dss.some(ds => ds.id === did)
    const visibleValue = isValid ? did : null
    setTrainSet(visibleValue)
    form.setFieldsValue({ datasetId: visibleValue })
  }, [allDatasets, project])

  useEffect(() => {
    did && func.getDataset(did)
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

  async function fetchProject() {
    const project = await func.getProject(pid)
    project && setProject(project)
    form.setFieldsValue({ keywords: project.keywords })
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
    // if (gpuCount) {
    config['gpu_count'] = gpuCount || 0
    // }
    const img = (form.getFieldValue('image') || '').split(',')
    const imageId = Number(img[0])
    const image = img[1]
    const params = {
      ...values,
      name: 'group_' + randomNumber(),
      projectId: pid,
      keywords: iterationId ? project.keywords : values.keywords,
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

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_train_' + randomNumber(),
    datasetId: did ? did : undefined,
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
          <CheckProjectDirty style={{ marginBottom: 20 }} pid={pid} initialCheck={true} callback={(dirty) => setProjectDirty(dirty)} />
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
                    { required: true, message: t('task.train.form.trainset.required') },
                  ]}
                >
                  <Select
                    placeholder={t('task.train.form.training.datasets.placeholder')}
                    filterOption={(input, option) => option.children.join('').toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    onChange={trainSetChange}
                    showArrow
                  >
                    {datasets.filter(ds => ds.id !== testSet).map(item =>
                      <Option value={item.id} key={item.id}>
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
                    { required: true, message: t('task.train.form.testset.required') },
                  ]}
                >
                  <Select
                    disabled={test}
                    placeholder={t('task.train.form.test.datasets.placeholder')}
                    filterOption={(input, option) => option.children.join('').toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    onChange={validationSetChange}
                    showArrow
                  >
                    {datasets.filter(ds => ds.id !== trainSet).map(item =>
                      <Option value={item.id} key={item.id}>
                        {item.name} {item.versionName}({item.assetCount})
                      </Option>
                    )}
                  </Select>
                </Form.Item>
              </Tip>
            </ConfigProvider>
            <Tip hidden={true}>
              <Form.Item label={t('dataset.train.form.samples')}>
                <KeywordRates dataset={trainSet}></KeywordRates>
              </Form.Item>
            </Tip>
            <Tip content={t('tip.task.filter.keywords')}>
              {iterationId ? <Form.Item label={t('task.train.form.keywords.label')}>
                {project?.keywords?.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}
              </Form.Item> :
              <Form.Item
                label={t('task.label.form.target.label')}
                name="keywords"
                rules={[
                  { required: true, message: t('task.label.form.target.placeholder') }
                ]}
              >
                <Select mode="multiple" showArrow
                  placeholder={t('task.label.form.member.labeltarget')}
                  filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}>
                  {keywords.map(keyword => (
                    <Select.Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                      <Row>
                        <Col flex={1}>{keyword.name}</Col>
                      </Row>
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item> }
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
                >
                  <InputNumber min={0} max={gpu_count} precision={0} /></Form.Item>
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
                    <Button type="primary" size="large" disabled={projectDirty} htmlType="submit">
                      {t('common.action.train')}
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
    keywords: state.keyword.keywords.items,
  }
}

const dis = (dispatch) => {
  return {
    getProject(id) {
      return dispatch({
        type: "project/getProject",
        payload: { id },
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
    getKeywords() {
      return dispatch({
        type: 'keyword/getKeywords',
        payload: { limit: 10000 },
      })
    },
  }
}

export default connect(props, dis)(Train)
