import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Button, Form, Row, Col, ConfigProvider, Space, InputNumber } from "antd"
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
import { TASKSTATES } from '@/constants/task'
import { TYPES } from '@/constants/image'
import { useHistory, useParams, useLocation } from "umi"
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyStateDataset from '@/components/empty/dataset'
import EmptyStateModel from '@/components/empty/model'
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"
import ImageSelect from "../components/imageSelect"

const { Option } = Select

const Algorithm = () => [{ id: "aldd", label: 'ALDD', checked: true }]
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

function Mining({ getDatasets, getModels, createMiningTask, getSysInfo }) {
  const { ids } = useParams()
  const datasetIds = ids ? ids.split('|').map(id => parseInt(id)) : []
  const history = useHistory()
  const location = useLocation()
  const { mid, image } = location.query
  const [datasets, setDatasets] = useState([])
  const [models, setModels] = useState([])
  const [selectedSets, setSelectedSets] = useState([])
  const [excludeSets, setExcludeSets] = useState([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [trainSetCount, setTrainSetCount] = useState(1)
  const [hpVisible, setHpVisible] = useState(false)
  const [topk, setTopk] = useState(false)
  const [gpu_count, setGPU] = useState(0)

  useEffect(() => {
    fetchSysInfo()
  }, [])

  useEffect(async () => {
    let result = await getDatasets({ limit: 100000 })
    if (result) {
      setDatasets(result.items.filter(dataset => TASKSTATES.FINISH === dataset.state))
    }
  }, [])

  useEffect(async () => {
    let result = await getModels({ limit: 100000 })
    if (result) {
      setModels(result.items)
    }
  }, [])

  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  useEffect(() => {
    setSelectedSets(datasetIds)
  }, [ids])

  useEffect(() => {
    if (datasets.length) {
      setTrainSetCount(datasets.reduce((prev, current) =>
        selectedSets.indexOf(current.id) > -1 ? prev + current.asset_count : prev,
        0) || 1)
    }
  }, [selectedSets, datasets])

  useEffect(() => {
    const state = location.state

    if (state?.record) {
      const { parameters, name, config, } = state.record
      const { include_datasets, exclude_datasets, strategy, top_k, model_id, generate_annotations, docker_image, docker_image_id } = parameters
      const sets = include_datasets || []
      const xsets = exclude_datasets || []
      setTopk(!!top_k)
      form.setFieldsValue({
        name: `${name}_${randomNumber()}`,
        datasets: sets,
        exclude_sets: xsets,
        filter_strategy: !!top_k,
        inference: generate_annotations,
        model: model_id,
        docker_image: docker_image_id + ',' + docker_image,
        topk: top_k,
        gpu_count: config.gpu_count,
        strategy,
      })
      setConfig(config)
      setSelectedSets(sets)
      setExcludeSets(xsets)
      setHpVisible(true)

      history.replace({ state: {} })
    }
  }, [location.state])

  function validHyperparam(rule, value) {

    const params = form.getFieldValue('hyperparam').map(({ key }) => key)
      .filter(item => item && item.trim() && item === value)
    if (params.length > 1) {
      return Promise.reject(t('task.validator.same.param'))
    } else {
      return Promise.resolve()
    }
  }

  async function fetchSysInfo() {
    const result = await getSysInfo()
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
    const img = (form.getFieldValue('docker_image') || '').split(',')
    const docker_image_id = Number(img[0])
    const docker_image = img[1]
    const params = {
      ...values,
      name: values.name.trim(),
      topk: values.filter_strategy ? values.topk : 0,
      docker_image,
      docker_image_id,
      config,
    }
    const result = await createMiningTask(params)
    if (result) {
      history.replace("/home/task")
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function setsChange(value) {
    setSelectedSets(value)
  }

  function excludeSetChange(value) {
    setExcludeSets(value)
  }

  function getImageIdOfSelectedModel() {
    const selectedModelId = form.getFieldValue('model')
    const selectedModel = models.find(model => model.id === selectedModelId)
    return selectedModel?.parameters?.docker_image_id
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_mining_' + randomNumber(),
    model: mid ? parseInt(mid) : undefined,
    docker_image: image ? parseInt(image) : undefined,
    datasets: datasetIds,
    algorithm: getCheckedValue(Algorithm()),
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
            labelAlign={'left'}
            colon={false}
            scrollToFirstError
          >
            <Tip hidden={true}>
            <Form.Item
              label={t('task.filter.form.name.label')}
              name='name'
              rules={[
                { required: true, whitespace: true, message: t('task.filter.form.name.placeholder') },
                { type: 'string', min: 2, max: 50 },
              ]}
            >
              <Input placeholder={t('task.filter.form.name.required')} autoComplete='off' allowClear />
            </Form.Item>
            </Tip>

            <ConfigProvider renderEmpty={() => <EmptyStateDataset add={() => history.push('/home/dataset/add')} />}>

            <Tip hidden={true}>
            <Form.Item
              label={t('task.filter.form.datasets.label')}
              required
              name="datasets"
              rules={[
                { required: true, message: t('task.filter.form.datasets.required') },
              ]}
            >
              <Select
                placeholder={t('task.filter.form.mining.datasets.placeholder')}
                mode='multiple'
                filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                onChange={setsChange}
                showArrow
              >
                {datasets.map(item => excludeSets.indexOf(item.id) < 0 ? (
                  <Option value={item.id} key={item.name}>
                    {item.name}({item.asset_count})
                  </Option>
                ) : null)}
              </Select>
            </Form.Item>
            </Tip>
            <Tip hidden={true}>
              <Form.Item name='strategy'
                hidden={selectedSets.length < 2}
                initialValue={2} label={t('task.train.form.repeatdata.label')}>
                <Radio.Group options={[
                  { value: 2, label: t('task.train.form.repeatdata.latest') },
                  { value: 3, label: t('task.train.form.repeatdata.original') },
                  { value: 1, label: t('task.train.form.repeatdata.terminate') },
                ]} />
              </Form.Item>
            </Tip>

              <Tip content={t('tip.task.filter.excludeset')}>
                <Form.Item
                  label={t('task.mining.form.excludeset.label')}
                  name="exclude_sets"
                >
                  <Select
                    placeholder={t('task.filter.form.exclude.datasets.placeholder')}
                    mode='multiple'
                    onChange={excludeSetChange}
                    filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    showArrow
                  >
                    {datasets.map(item => selectedSets.indexOf(item.id) < 0 ? (
                      <Option value={item.id} key={item.name}>
                        {item.name}({item.asset_count})
                      </Option>
                    ) : null)}
                  </Select>
                </Form.Item>
              </Tip>
            </ConfigProvider>


            <ConfigProvider renderEmpty={() => <EmptyStateModel />}>
              <Tip content={t('tip.task.filter.model')}>
                <Form.Item
                  label={t('task.mining.form.model.label')}
                  name="model"
                  rules={[
                    { required: true, message: t('task.mining.form.model.required') },
                  ]}
                >
                  <Select
                    placeholder={t('task.mining.form.mining.model.required')}
                    filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    showArrow
                  >
                    {models.map(item => (
                      <Option value={item.id} key={item.name}>
                        {item.name}(id: {item.id})
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Tip>
            </ConfigProvider>

            <Tip content={t('tip.task.mining.image')}>
              <Form.Item name='docker_image' label={t('task.train.form.image.label')} rules={[
                {required: true, message: t('task.train.form.image.required')}
              ]}>
                <ImageSelect placeholder={t('task.train.form.image.placeholder')} relatedId={getImageIdOfSelectedModel()} type={TYPES.MINING} onChange={imageChange} />
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item
                label={t('task.mining.form.algo.label')}
                name="algorithm"
              >
                {renderRadio(Algorithm())}
              </Form.Item>
            </Tip>

            <Tip content={t('tip.task.filter.strategy')}>
              <Form.Item
                label={t('task.mining.form.strategy.label')}
              >
                <Form.Item
                  name='filter_strategy'
                  initialValue={topk}
                  noStyle
                >
                  <Radio.Group onChange={filterStrategyChange}>
                    <Radio value={false}>{t('common.all')}</Radio>
                    <Radio checked value={true}>{t('task.mining.form.topk.label')}</Radio>
                    <Form.Item noStyle name='topk' label='topk' dependencies={['filter_strategy']} rules={topk ? [
                      { type: 'number', min: 1, max: trainSetCount - 1 || 1 }
                    ] : null}>
                      <InputNumber style={{ width: 120 }} min={1} max={trainSetCount - 1} precision={0} disabled={!topk} />
                    </Form.Item>
                  </Radio.Group>
                </Form.Item>
                <p style={{ display: 'inline-block', marginLeft: 10 }}>{t('task.mining.topk.tip')}</p>
              </Form.Item>
            </Tip>

            <Tip content={t('tip.task.filter.newlable')}>
              <Form.Item
                label={t('task.mining.form.label.label')}
                name='inference'
                initialValue={false}
              >
                <Radio.Group options={[
                  { value: true, label: t('common.yes') },
                  { value: false, label: t('common.no') },
                ]} />
              </Form.Item>
            </Tip>

            <Tip content={t('tip.task.filter.mgpucount')}>
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

            {seniorConfig.length ? <Tip content={t('tip.task.filter.mhyperparams')}>
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
            </Tip> : null }
            <Tip hidden={true}>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit" disabled={!gpu_count}>
                    {t('task.filter.create')}
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

const dis = (dispatch) => {
  return {
    getSysInfo() {
      return dispatch({
        type: "common/getSysInfo",
      })
    },
    getModels: (payload) => {
      return dispatch({
        type: 'model/getModels',
        payload,
      })
    },
    getDatasets(payload) {
      return dispatch({
        type: "dataset/getDatasets",
        payload,
      })
    },
    createMiningTask(payload) {
      return dispatch({
        type: "task/createMiningTask",
        payload,
      })
    },
  }
}

export default connect(null, dis)(Mining)
