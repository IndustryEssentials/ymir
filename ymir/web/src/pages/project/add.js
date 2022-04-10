import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Radio, Row, Col, InputNumber, ConfigProvider } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory, useLocation } from "umi"

import s from './add.less'
import t from '@/utils/t'
import { MiningStrategy } from '@/constants/project'
import Breadcrumbs from '@/components/common/breadcrumb'
import Tip from '@/components/form/tip'
import EmptyState from '@/components/empty/dataset'
import DatasetSelect from '../../components/form/datasetSelect'
import Panel from '../../components/form/panel'

const { useForm } = Form

const strategyOptions = Object.values(MiningStrategy)
  .filter(key => Number.isInteger(key))
  .map(value => ({
    value,
    label: t(`project.mining.strategy.${value}`),
  }))

const Add = ({ keywords, datasets, projects, getProject, getKeywords, ...func }) => {
  const { id } = useParams()
  const history = useHistory()
  const location = useLocation()
  const { settings } = location.query
  const [form] = useForm()
  const [settingsVisible, setSettingsVisible] = useState(true)
  const [isEdit, setEdit] = useState(false)
  const [project, setProject] = useState({ id })

  const [testSet, setTestSet] = useState(0)
  const [miningSet, setMiningSet] = useState(0)
  const [strategy, setStrategy] = useState(0)

  useEffect(() => {
    setEdit(!!id)

    id && fetchProject()
  }, [id])

  useEffect(() => {
    if (projects[id]) {
      setProject(projects[id])
    }
  }, [projects[id]])

  useEffect(() => {
    getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    initForm(project)
  }, [project])

  function initForm(project = {}) {
    const { name, keywords: kws, targetMap, targetDataset, targetIteration,
      description, testSet: testDataset, miningSet: miningDataset, miningStrategy, chunkSize } = project
    if (name) {
      form.setFieldsValue({
        name, keywords: kws, description,
        targetMap,
        targetIteration,
        targetDataset,
        testSet: testDataset?.id,
        miningSet: miningDataset?.id,
        strategy: miningStrategy || 0,
        chunkSize: miningStrategy === 0 && chunkSize ? chunkSize : undefined,
      })
    }
  }

  const submit = async ({ name = '', description = '', ...values }) => {
    const action = isEdit ? 'update' : 'create'
    var params = {
      ...values,
      chunkSize: strategy === 0 ? values.chunkSize : undefined,
    }
    if (settings || isEdit) {
      params.id = id
    }
    if (!settings) {
      params.name = name.trim()
      params.description = description.trim()
    }
    const result = await func[`${action}Project`](params)
    if (result) {
      const pid = result.id || id
      message.success(t(`project.${action}.success`))
      history.push(`/home/project/detail/${pid}`)
    }
  }

  const checkProjectName = (_, value) => {
    const reg = /^[a-zA-Z0-9]+(?:[._-][a-zA-Z0-9]+)*$/
    if (!value || reg.test(value.trim())) {
      return Promise.resolve()
    }
    return Promise.reject(t('project.add.form.name.invalid'))
  }

  async function fetchProject() {
    const result = await getProject(id)
  }

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.project.add')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 4 }} onFinish={submit} scrollToFirstError>
            {!settings ? <Panel hasHeader={false}>
              <Tip hidden={true}>
                <Form.Item
                  label={t('project.add.form.name')}
                  name='name'
                  rules={[
                    { required: true, message: t('project.add.form.name.required') },
                    { validator: checkProjectName },
                  ]}
                >
                  <Input placeholder={t('project.add.form.name.placeholder')} autoComplete='off' allowClear />
                </Form.Item>
              </Tip>
              <Tip hidden={true}>
                <Form.Item
                  label={t('project.add.form.type')}
                  name='type'
                  initialValue={0}
                >
                  <Radio.Group>
                    <Radio value={0}>{t('task.train.form.traintypes.detect')}</Radio>
                  </Radio.Group>
                </Form.Item>
              </Tip>
              <Tip hidden={true}>
                <Form.Item
                  label={t('project.add.form.keyword.label')}
                  name="keywords"
                  rules={[
                    { required: true, message: t('project.add.form.keyword.required') }
                  ]}
                >
                  <Select mode="multiple" showArrow
                    placeholder={t('project.add.form.keyword.placeholder')}
                    disabled={isEdit}
                    filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}>
                    {keywords.map(keyword => (
                      <Select.Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                        <Row>
                          <Col flex={1}>{keyword.name}</Col>
                        </Row>
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Tip>
              <Tip hidden={true}>
                <Form.Item label={t('project.add.form.target')}>
                  <div className={s.targetPanel}>
                    <Form.Item labelCol={{ span: 3 }} colon={false} labelAlign='left' label={t('project.add.form.target.map')} name='targetMap'>
                      <InputNumber min={0} max={100} step={1} precision={2} formatter={value => `${value}%`} parser={value => value.replace('%', '')} style={{ width: '100%' }} placeholder={t('project.add.form.target.map.placeholder')} allowClear />
                    </Form.Item>
                    <Form.Item labelCol={{ span: 3 }} colon={false} labelAlign='left' label={t('project.add.form.target.iterations')} name='targetIteration'>
                      <InputNumber min={1} step={1} precision={0} max={100} placeholder={t('project.add.form.target.iterations.placeholder')} style={{ width: '100%' }} allowClear />
                    </Form.Item>
                    <Form.Item labelCol={{ span: 3 }} colon={false} labelAlign='left' label={t('project.add.form.target.dataset')} name='targetDataset'>
                      <InputNumber min={1} step={1} precision={0} max={100000000} placeholder={t('project.add.form.target.dataset.placeholder')} style={{ width: '100%' }} allowClear />
                    </Form.Item>
                  </div>
                </Form.Item>
              </Tip>
              <Tip hidden={true}>
                <Form.Item label={t('project.add.form.desc')} name='description'
                  rules={[
                    { max: 500 },
                  ]}
                >
                  <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
                </Form.Item>
              </Tip>
            </Panel> : null}
            {isEdit ? <Panel label={t('project.iteration.settings.title')} visible={settingsVisible} setVisible={() => setSettingsVisible(!settingsVisible)}>
              <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push(`/home/dataset/add/${id}`)} />}>
                <Tip hidden={true}>
                  <Form.Item label={t('project.add.form.training.set')}>
                    {project.trainSet?.name}
                  </Form.Item>
                </Tip>
                <Tip hidden={true}>
                  <Form.Item label={t('project.add.form.test.set')} name="testSet" rules={[
                    { required: true, message: t('task.train.form.testset.required') },
                  ]}>
                    <DatasetSelect pid={id} filter={[miningSet]} onChange={(value) => value && setTestSet(value)} />
                  </Form.Item>
                </Tip>
                <Tip hidden={true}>
                  <Form.Item label={t('project.add.form.mining.set')} name="miningSet" 
                  rules={[
                    { required: true, message: t('task.train.form.miningset.required') },
                  ]}>
                    <DatasetSelect pid={id} filter={[project?.trainSet?.id, testSet]} onChange={(value) => value && setMiningSet(value)} />
                  </Form.Item>
                </Tip>
                <Tip hidden={true}>
                  <Form.Item label={t('project.add.form.mining.strategy')}>
                    <Row>
                      <Col flex={1}>
                        <Form.Item name='strategy' noStyle>
                          <Select options={strategyOptions} onChange={value => setStrategy(value)} />
                        </Form.Item>
                      </Col>
                      {strategy === 0 ? <Col flex={'200px'} offset={1}>
                        <Form.Item label={t('project.add.form.mining.chunksize')} 
                          wrapperCol={{ span: 12 }} labelCol={{ span: 12 }} name='chunkSize'
                          rules={[
                            { required: strategy === 0 }
                          ]}>
                          <InputNumber step={1} min={1} style={{ width: '100%' }} />
                        </Form.Item>
                      </Col> : null}
                    </Row>
                  </Form.Item>
                </Tip>
              </ConfigProvider>
            </Panel> : null}
            <Tip hidden={true}>
              <Form.Item wrapperCol={{ offset: 4 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit">
                      {isEdit ? t('common.confirm') : t('project.add.submit')}
                    </Button>
                  </Form.Item>
                  <Form.Item name='backBtn' noStyle>
                    <Button size="large" onClick={() => history.goBack()}>
                      {t('common.back')}
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
    keywords: state.keyword.keywords.items,
    datasets: state.project.datasets,
    projects: state.project.projects,
  }
}

const actions = (dispatch) => {
  return {
    createProject: (payload) => {
      return dispatch({
        type: 'project/createProject',
        payload,
      })
    },
    updateProject: (payload) => {
      return dispatch({
        type: 'project/updateProject',
        payload,
      })
    },
    getProject: (id) => {
      return dispatch({
        type: 'project/getProject',
        payload: { id },
      })
    },
    getKeywords(payload) {
      return dispatch({
        type: 'keyword/getKeywords',
        payload,
      })
    },
  }
}

export default connect(props, actions)(Add)
