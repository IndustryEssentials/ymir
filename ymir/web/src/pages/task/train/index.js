import React, { useEffect, useRef, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Checkbox, Button, Form, Row, Col, ConfigProvider, Space, InputNumber, Tag } from "antd"
import {
  PlusOutlined,
  MinusCircleOutlined,
  UpSquareOutlined,
  DownSquareOutlined,
} from '@ant-design/icons'
import { formLayout } from "@/config/antd"
import { useHistory, useParams, useLocation } from "umi"

import TripleRates from "@/components/form/tripleRates"
import t from "@/utils/t"
import { TASKSTATES } from '@/constants/task'
import { CONFIGTYPES } from '@/constants/mirror'
import Breadcrumbs from "../../../components/common/breadcrumb"
import EmptyState from '@/components/empty/dataset'
import styles from "./index.less"
import commonStyles from "../common.less"
import { AddDelTwoIcon } from '@/components/common/icons'
import { randomNumber } from "../../../utils/number"

const { Option } = Select

const TrainType = () => [{ id: "detection", label: t('task.train.form.traintypes.detect'), checked: true }]
const FrameworkType = () => [{ id: "YOLO v4", label: "YOLO v4", checked: true }]
const Backbone = () => [{ id: "darknet", label: "Darknet", checked: true }]

function Train({ getDatasets, createTrainTask, getRuntimes }) {
  const { ids } = useParams()
  const datasetIds = ids ? ids.split('|').map(id => parseInt(id)) : []
  const history = useHistory()
  const location = useLocation()
  const [datasets, setDatasets] = useState([])
  const [trainSets, setTrainSets] = useState([])
  const [validationSets, setValidationSets] = useState([])
  const [keywords, setKeywords] = useState([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [hpVisible, setHpVisible] = useState(false)
  const hpMaxSize = 30

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

  useEffect(async () => {
    let result = await getDatasets({ limit: 100000 })
    if (result) {
      setDatasets(result.items.filter(dataset => TASKSTATES.FINISH === dataset.state))
    }
  }, [])

  useEffect(() => {
    let getKw = (sets) => {
      let kw = datasets.reduce((prev, curr) => sets.indexOf(curr.id) >= 0 ? prev.concat(curr.keywords) : prev, [])
      kw = [...new Set(kw)]
      kw.sort()
      return kw
    }
    const tkw = getKw(trainSets)
    const vkw = getKw(validationSets)
    // console.log('keywords: ', tkw, vkw)
    const kws = tkw.filter(v => vkw.includes(v))
    setKeywords(kws)
  }, [trainSets, validationSets, datasets])

  useEffect(async () => {
    const result = await getRuntimes({ type: CONFIGTYPES.TRAINING })
    if (result && !(location.state && location.state.record)) {
      setConfig(result.config)
    }
  }, [])
  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  useEffect(() => {
    setTrainSets(datasetIds)
  }, [ids])

  useEffect(() => {
    const state = location.state
    console.log('state: ', state)

    if (state?.record) {
      const { parameters, name, config, } = state.record
      const { include_classes, include_train_datasets, include_validation_datasets, strategy, } = parameters
      //do somethin
      form.setFieldsValue({
        name: `${name}_${randomNumber()}`,
        train_sets: include_train_datasets,
        validation_sets: include_validation_datasets,
        gpu_count: config.gpu_count,
        keywords: include_classes,
        strategy,
      })
      setConfig(config)
      setTrainSets(include_train_datasets)
      setValidationSets(include_validation_datasets)
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

  function trainSetChange(value) {
    // console.log('change: ', value)
    setTrainSets(value)
    form.setFieldsValue({ keywords: [] })
  }
  function validationSetChange(value) {
    setValidationSets(value)
    form.setFieldsValue({ keywords: [] })
  }

  function setConfig(config) {
    const params = Object.keys(config).map(key => ({ key, value: config[key] }))
    setSeniorConfig(params)
  }

  const onFinish = async (values) => {
    const config = {}
    form.getFieldValue('hyperparam').forEach(({ key, value }) => key && value ? config[key] = value : null)

    const gpuCount = form.getFieldValue('gpu_count')
    if (gpuCount) {
      config['gpu_count'] = gpuCount
    }
    const params = {
      ...values,
      name: values.name.trim(),
      config,
    }
    const result = await createTrainTask(params)
    if (result) {
      history.replace("/home/task")
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_train_' + randomNumber(),
    train_sets: datasetIds,
    train_type: getCheckedValue(TrainType()),
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
            size='large'
            colon={false}
          >
            <Form.Item
              label={t('task.filter.form.name.label')}
              name='name'
              rules={[
                { required: true, whitespace: true, message: t('task.filter.form.name.placeholder') },
                { type: 'string', min: 2, max: 20 },
              ]}
            >
              <Input placeholder={t('task.filter.form.name.required')} autoComplete='off' allowClear />
            </Form.Item>
            <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push('/home/dataset/add')} />}>
              <Form.Item
                label={t('task.train.form.trainsets.label')}
              >
                <Form.Item
                  noStyle
                  name="train_sets"
                  rules={[
                    { required: true, message: t('task.filter.form.datasets.required') },
                  ]}
                >
                  <Select
                    placeholder={t('task.filter.form.datasets.placeholder')}
                    mode='multiple'
                    filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                    onChange={trainSetChange}
                    showArrow
                  >
                    {datasets.map(item => validationSets.indexOf(item.id) < 0 ? (
                      <Option value={item.id} key={item.name}>
                        {item.name}({item.asset_count})
                      </Option>
                    ) : null)}
                  </Select>
                </Form.Item>
                <div className={commonStyles.formItemLowLevel}>
                  <span className={commonStyles.label}>{t('task.train.form.repeatdata.label')}</span>
                  <Form.Item name='strategy' colon={true} initialValue={2} noStyle>
                    <Radio.Group options={[
                      { value: 2, label: t('task.train.form.repeatdata.latest') },
                      { value: 3, label: t('task.train.form.repeatdata.original') },
                      { value: 1, label: t('task.train.form.repeatdata.terminate') },
                    ]} />
                  </Form.Item></div>
              </Form.Item>
              <Form.Item
                label={t('task.train.form.testsets.label')}
                name="validation_sets"
                rules={[
                  { required: true, message: t('task.filter.form.datasets.required') },
                ]}
              >
                <Select
                  placeholder={t('task.filter.form.datasets.placeholder')}
                  mode='multiple'
                  filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                  onChange={validationSetChange}
                  showArrow
                >
                  {datasets.map(item => trainSets.indexOf(item.id) < 0 ? (
                    <Option value={item.id} key={item.name}>
                      {item.name}({item.asset_count})
                    </Option>
                  ) : null)}
                </Select>
              </Form.Item>
            </ConfigProvider>
            <Form.Item wrapperCol={{ offset: 4, span: 12 }} hidden={![...trainSets, ...validationSets].length}>
              <TripleRates
                data={datasets}
                parts={[
                  { ids: trainSets, label: t('task.train.form.trainsets.label') },
                  { ids: validationSets, label: t('task.train.form.testsets.label') },
                ]}
              ></TripleRates>
            </Form.Item>
            <Form.Item
              label={t('task.train.form.keywords.label')}
              // next version
              // >
              //   <Form.Item
              name="keywords"
              rules={[
                { required: true, message: t('task.train.form.keywords.required') }
              ]}
            >
              <Select mode="multiple" showArrow placeholder={t('task.train.keywords.placeholder')}>
                {keywords.map(keyword => (
                  <Option key={keyword} value={keyword}>
                    {keyword}
                  </Option>
                ))}
              </Select>
              {/* next version */}
              {/* </Form.Item>
              <div className={styles.formItemLowLevel}><span className={styles.label}>{t('常用标签: ')}</span><Form.Item name='label_strategy' colon={true} initialValue={0} noStyle>
                <Tag>cat</Tag>
                <Tag>dog</Tag>
                <Tag>person</Tag>
                <Tag>pig</Tag>
              </Form.Item></div> */}
            </Form.Item>
            <Form.Item
              label={t('task.train.form.traintype.label')}
              name="train_type"
            >
              {renderRadio(TrainType())}
            </Form.Item>
            <Form.Item
              label={t('task.train.form.network.label')}
              name="network"
            >
              {renderRadio(FrameworkType())}
            </Form.Item>
            <Form.Item
              label={t('task.train.form.backbone.label')}
              name="backbone"
            >
              {renderRadio(Backbone())}
            </Form.Item>
            <Form.Item
              label={t('task.gpu.count')}
              name="gpu_count"
              rules={[{ type: 'number', min: 1, max: 1000 }]}
            >
              <InputNumber min={1} max={1000} precision={0} />
            </Form.Item>
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

              {hpVisible ? <Form.List name='hyperparam'>
                {(fields, { add, remove }) => (
                  <>
                    <div className={styles.paramContainer}>
                      <Row style={{ backgroundColor: '#fafafa', border: '1px solid #f4f4f4', lineHeight: '40px', marginBottom: 10 }} gutter={20}>
                        <Col flex={'240px'}>Key</Col>
                        <Col flex={1}>Value</Col>
                        <Col span={2}>Action</Col>
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
              </Form.List> : null}

            </Form.Item>
            <Form.Item wrapperCol={{ offset: 4 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
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
          </Form>
        </div>
      </Card>
    </div>
  )
}

const dis = (dispatch) => {
  return {
    getDatasets(payload) {
      return dispatch({
        type: "dataset/getDatasets",
        payload,
      })
    },
    createTrainTask(payload) {
      return dispatch({
        type: "task/createTrainTask",
        payload,
      })
    },
    getRuntimes(payload) {
      return dispatch({
        type: "common/getRuntimes",
        payload,
      })
    },
  }
}

export default connect(null, dis)(Train)
