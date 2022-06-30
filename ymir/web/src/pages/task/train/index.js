import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Button, Form, Row, Col, ConfigProvider, Space, InputNumber, Tag, message } from "antd"
import { formLayout } from "@/config/antd"
import { useHistory, useParams, useLocation } from "umi"

import t from "@/utils/t"
import { string2Array } from '@/utils/string'
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
import LiveCodeForm from "../components/liveCodeForm"
import { removeLiveCodeConfig } from "../components/liveCodeConfig"
import DockerConfigForm from "../components/dockerConfigForm"
import useFetch from '@/hooks/useFetch'

const { Option } = Select

const TrainType = [{ value: "detection", label: 'task.train.form.traintypes.detect', checked: true }]
const FrameworkType = [{ value: "YOLO v4", label: "YOLO v4", checked: true }]
const Backbone = [{ value: "darknet", label: "Darknet", checked: true }]
const TrainDevices = [
  { value: false, label: 'task.train.device.local', checked: true, },
  { value: true, label: 'task.train.device.openpai', },
]

function Train({ allDatasets, datasetCache, keywords, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { mid, image, iterationId, outputKey, currentStage, test } = location.query
  const stage = string2Array(mid)
  const did = Number(location.query.did)
  const [project, setProject] = useState({})
  const [datasets, setDatasets] = useState([])
  const [dataset, setDataset] = useState({})
  const [trainSet, setTrainSet] = useState(null)
  const [testSet, setTestSet] = useState(null)
  const [testingSetIds, setTestingSetIds] = useState([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [gpu_count, setGPU] = useState(0)
  const [projectDirty, setProjectDirty] = useState(false)
  const [live, setLiveCode] = useState(false)
  const [openpai, setOpenpai] = useState(false)
  const [sys, getSysInfo] = useFetch('common/getSysInfo', {})

  const renderRadio = (types) => <Radio.Group options={types.map(type => ({ ...type, label: t(type.label) }))} />

  useEffect(() => {
    getSysInfo()
    fetchProject()
  }, [])

  useEffect(() => {
    setGPU(sys.gpu_count)
    setOpenpai(!!sys.openpai_enabled)
  }, [sys])

  useEffect(() => {
    form.setFieldsValue({ openpai: openpai })
  }, [openpai])

  useEffect(() => {
    func.getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    const dss = allDatasets.filter(ds => ds.keywords.some(kw => project?.keywords?.includes(kw)))
    setDatasets(dss)
    const isValid = dss.some(ds => ds.id === did)
    const visibleValue = isValid ? did : null
    setTrainSet(visibleValue)
    setTestingSetIds(project?.testingSets || [])
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

  function imageChange(_, image = {}) {
    const { configs } = image
    const configObj = (configs || []).find(conf => conf.type === TYPES.TRAINING) || {}
    setLiveCode(image.liveCode || false)
    setConfig(removeLiveCodeConfig(configObj.config))
  }

  function setConfig(config = {}) {
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
      history.replace(`/home/project/${pid}/model`)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["value"]
  const initialValues = {
    name: 'task_train_' + randomNumber(),
    datasetId: did ? did : undefined,
    testset: Number(test) ? Number(test) : undefined,
    image: image ? parseInt(image) : undefined,
    modelStage: stage,
    trainType: getCheckedValue(TrainType),
    network: getCheckedValue(FrameworkType),
    backbone: getCheckedValue(Backbone),
    openpai: getCheckedValue(TrainDevices),
    gpu_count: 1,
  }
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.training')}>
        <div className={commonStyles.formContainer}>
          <CheckProjectDirty style={{ marginBottom: 20, width: '100%' }} pid={pid} initialCheck={true} callback={(dirty) => setProjectDirty(dirty)} />
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
                    {datasets.filter(ds => ds.id !== testSet && !testingSetIds.includes(ds.id)).map(item =>
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
                  label={t('task.train.form.keywords.label')}
                  name="keywords"
                  rules={[
                    { required: true, message: t('project.add.form.keyword.required') }
                  ]}
                >
                  <Select mode="multiple" showArrow
                    placeholder={t('project.add.form.keyword.required')}
                    filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}>
                    {keywords.map(keyword => (
                      <Select.Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                        <Row>
                          <Col flex={1}>{keyword.name}</Col>
                        </Row>
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>}
            </Tip>
            {openpai ? <Tip hidden={true}>
              <Form.Item label={t('task.train.form.platform.label')} name='openpai'>
                {renderRadio(TrainDevices)}
              </Form.Item>
            </Tip> : null }
            <ConfigProvider renderEmpty={() => <EmptyStateModel id={pid} />}>
              <Tip content={t('tip.task.train.model')}>
                <Form.Item
                  label={t('task.mining.form.model.label')}
                  name="modelStage"
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
                {renderRadio(TrainType)}
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item
                label={t('task.train.form.network.label')}
                name="network"
              >
                {renderRadio(FrameworkType)}
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item
                label={t('task.train.form.backbone.label')}
                name="backbone"
              >
                {renderRadio(Backbone)}
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

            <LiveCodeForm live={live} />
            <DockerConfigForm seniorConfig={seniorConfig} form={form} />
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
