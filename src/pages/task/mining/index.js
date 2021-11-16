import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Card, Input, Radio, Checkbox, Button, Form, Row, Col, ConfigProvider, Space, InputNumber } from "antd"
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
import { CONFIGTYPES } from '@/constants/mirror'
import { useHistory, useParams, useLocation } from "umi"
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyStateDataset from '@/components/empty/dataset'
import EmptyStateModel from '@/components/empty/model'
import { randomNumber } from "../../../utils/number"

const { Option } = Select

const Algorithm = () => [{ id: "ladd", label: 'LADD', checked: true }]
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

function Mining({ getDatasets, getModels, createMiningTask, getRuntimes }) {
  const { ids } = useParams()
  const datasetIds = ids ? ids.split('|').map(id => parseInt(id)) : []
  const history = useHistory()
  const location = useLocation()
  const { mid } = location.query
  const [datasets, setDatasets] = useState([])
  const [models, setModels] = useState([])
  const [selectedSets, setSelectedSets] = useState([])
  const [excludeSets, setExcludeSets] = useState([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState([])
  const [trainSetCount, setTrainSetCount] = useState(1)
  const [hpVisible, setHpVisible] = useState(false)
  const hpMaxSize = 30


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

  useEffect(async () => {
    const result = await getRuntimes({ type: CONFIGTYPES.MINING })
    if (result) {
      const params = Object.keys(result.config).map(key => ({ key, value: result.config[key] }))
      setSeniorConfig(params)
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
      0))
    }
  }, [selectedSets, datasets])

  function validHyperparam(rule, value) {

    const params = form.getFieldValue('hyperparam').map(({ key }) => key)
      .filter(item => item && item.trim() && item === value)
    if (params.length > 1) {
      return Promise.reject('Same Key Above')
    } else {
      return Promise.resolve()
    }
  }

  const onFinish = async (values) => {
    const config = {}
    form.getFieldValue('hyperparam').forEach(({ key, value }) => key && value ? config[key] = value : null)

    const params = {
      ...values,
      name: values.name.trim(),
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

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_mining_' + randomNumber(),
    model: mid ? parseInt(mid) : undefined,
    datasets: datasetIds,
    algorithm: getCheckedValue(Algorithm()),
    topk: 0,
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
            <ConfigProvider renderEmpty={() => <EmptyStateDataset add={() => history.push({ pathname: '/home/dataset', state: { type: 'add' }})} />}>
              <Form.Item
                label={t('task.filter.form.datasets.label')}
                name="datasets"
                rules={[
                  { required: true, message: t('task.filter.form.datasets.required') },
                ]}
              >
                <Select
                  placeholder={t('task.filter.form.datasets.placeholder')}
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
              <Form.Item
                label={t('task.mining.form.excludeset.label')}
                name="exclude_sets"
              >
                <Select
                  placeholder={t('task.filter.form.datasets.placeholder')}
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
            </ConfigProvider>
            <ConfigProvider renderEmpty={() => <EmptyStateModel />}>
              <Form.Item
                label={t('task.mining.form.model.label')}
                name="model"
                rules={[
                  { required: true, message: t('task.mining.form.model.required') },
                ]}
              >
                <Select
                  placeholder={t('task.mining.form.model.required')}
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
            </ConfigProvider>
            <Form.Item
              label={t('task.mining.form.algo.label')}
              name="algorithm"
            >
              {renderRadio(Algorithm())}
            </Form.Item>
            <Form.Item
              label={t('task.mining.form.strategy.label')}
            >
              <Radio checked>{t('task.mining.form.topk.label')}</Radio>
              <Form.Item noStyle name='topk' label='topk' rules={[
                { type: 'number', min: 1, max: trainSetCount || 1}
              ]}>
                <InputNumber style={{ width: 120 }} min={1} max={trainSetCount} precision={0} />
              </Form.Item>
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
                  <div className={styles.paramContainer}>
                    <Row style={{ backgroundColor: '#fafafa', lineHeight: '40px', marginBottom: 10 }} gutter={20}>
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
                            {field.name === fields.length - 1 ? <PlusOutlined onClick={() => add()} title={t('task.train.parameter.add.label')}  /> : null }
                          </Space>
                        </Col>
                      </Row>
                    ))}

                  </div>
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
    getRuntimes(payload) {
      return dispatch({
        type: "common/getRuntimes",
        payload,
      })
    },
  }
}

export default connect(null, dis)(Mining)
