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
const { confirm } = Modal

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
    const { name, keywords: kws, trainSetVersion,
      description, testSet: testDataset, miningSet: miningDataset, miningStrategy, chunkSize } = project
    if (name) {
      form.setFieldsValue({
        name, keywords: kws, description,
        trainSetVersion,
        testSet: testDataset?.id,
        miningSet: miningDataset?.id,
        strategy: miningStrategy || 0,
        chunkSize: miningStrategy === 0 && chunkSize ? chunkSize : undefined,
      })
      setStrategy(miningStrategy)
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
      params.name = (name || '').trim()
      params.description = (description || '').trim()
    }

    const send = async () => {
      const result = await func[`${action}Project`](params)
      if (result) {
        const pid = result.id || id
        message.success(t(`project.${action}.success`))
        history.push(`/home/project/detail/${pid}`)
      }
    }
    // edit project
    if (isEdit) {
      return send()
    }
    // create project
    const kws = params.keywords.map(kw => (kw || '').trim()).filter(kw => kw)
    const { failed } = await func.checkKeywords(kws)
    const newKws = kws.filter(keyword => !failed.includes(keyword))

    if (newKws?.length) {
      // confirm
      confirm({
        title: t('project.add.confirm.title'),
        content: <ol>{newKws.map(keyword => <li key={keyword}>{keyword}</li>)}</ol>,
        onOk: () => {
          addNewKeywords(newKws, send)
        },
        okText: t('project.add.confirm.ok'),
        cancelText: t('project.add.confirm.cancel'),
      })
    } else {
      send()
    }
  }


  const addNewKeywords = async (keywords, callback = () => { }) => {
    const result = func.addKeywords(keywords)
    if (result) {
      setTimeout(() => callback(), 500)
    }
  }

  async function fetchProject() {
    const result = await getProject(id)
  }

  function validateKeywords(_, kws) {
    if (kws?.length) {
      const valid = kws.every(kw => (kw || '').trim())
      if (!valid) {
        return Promise.reject(t('project.keywords.invalid'))
      }
    }
    return Promise.resolve()
  }

  const renderTitle = t(`breadcrumbs.project.${isEdit ? 'edit' : 'add'}`)

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={renderTitle}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 6, offset: 2 }} wrapperCol={{ span: 12 }} labelAlign='left' onFinish={submit} scrollToFirstError>
            {!settings ? <Panel hasHeader={false}>
                <Form.Item
                  label={t('project.add.form.name')}
                  name='name'
                  rules={[
                    { required: true, whitespace: true, message: t('project.add.form.name.required') },
                    { min: 1, max: 100 },
                  ]}
                >
                  <Input placeholder={t('project.add.form.name.placeholder')} autoComplete='off' allowClear />
                </Form.Item>
                <Form.Item
                  label={t('project.add.form.type')}
                  name='type'
                  initialValue={0}
                >
                  <Radio.Group>
                    <Radio value={0}>{t('task.train.form.traintypes.detect')}</Radio>
                  </Radio.Group>
                </Form.Item>
                <Form.Item
                  label={t('project.train_classes')}
                  name="keywords"
                  rules={[
                    { required: true, message: t('project.add.form.keyword.required') },
                    { validator: validateKeywords },
                  ]}
                  tooltip={t('project.add.form.keyword.tip')}
                >
                  <Select mode="tags" showArrow tokenSeparators={[',']}
                    placeholder={t('project.add.form.keyword.placeholder')}
                    disabled={isEdit && project?.currentIteration?.id}
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
                <Form.Item label={t('project.add.form.desc')} name='description'
                  rules={[
                    { max: 500 },
                  ]}
                >
                  <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
                </Form.Item>
            </Panel> : null}
            {isEdit ? <Panel label={t('project.iteration.settings.title')} visible={settingsVisible} setVisible={() => setSettingsVisible(!settingsVisible)}>
              <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push(`/home/dataset/add/${id}`)} />}>
                  <Form.Item label={t('project.add.form.training.set')} tooltip={t('project.add.trainset.tip')}>
                    {project.trainSet?.name}
                    <Form.Item noStyle name='trainSetVersion'>
                      <Select style={{ marginLeft: 20, width: 150 }} disabled={project.currentIteration}>
                        {project?.trainSet?.versions?.map(({ id, versionName, assetCount }) =>
                          <Select.Option key={id} value={id}>{versionName} (assets: {assetCount})</Select.Option>
                        )}
                      </Select>
                    </Form.Item>
                  </Form.Item>
                  <Form.Item label={t('project.add.form.test.set')} name="testSet" rules={[
                    { required: true, message: t('task.train.form.testset.required') },
                  ]} tooltip={t('project.add.testset.tip')}>
                    <DatasetSelect
                      pid={id}
                      filter={[miningSet]}
                      filterGroup={[project?.trainSet?.id, project?.miningSet?.groupId]}
                      filters={datasets => datasets.filter(ds => ds.keywords.some(kw => project?.keywords?.includes(kw)))}
                      onChange={(value) => setTestSet(value)}
                      allowClear
                    />
                  </Form.Item>
                  <Form.Item label={t('project.add.form.mining.set')} name="miningSet"
                    rules={[
                      { required: true, message: t('task.train.form.miningset.required') },
                    ]} tooltip={t('project.add.miningset.tip')}>
                    <DatasetSelect
                      pid={id}
                      filter={[testSet]}
                      filterGroup={[project?.trainSet?.id, project?.testSet?.groupId]}
                      onChange={(value) => setMiningSet(value)}
                      allowClear
                    />
                  </Form.Item>
                  <Form.Item label={t('project.add.form.mining.strategy')}>
                    <Row wrap={false}>
                      <Col flex={1}>
                        <Form.Item name='strategy' noStyle>
                          <Select options={strategyOptions} onChange={value => setStrategy(value)} />
                        </Form.Item>
                      </Col>
                      {strategy === 0 ? <Col flex={'200px'} offset={1}>
                        <Form.Item label={t('project.add.form.mining.chunksize')}
                          name='chunkSize'
                          rules={[
                            { required: strategy === 0 }
                          ]}>
                          <InputNumber step={1} min={1} style={{ width: '100%' }} />
                        </Form.Item>
                      </Col> : null}
                    </Row>
                  </Form.Item>
              </ConfigProvider>
            </Panel> : null}
              <Form.Item wrapperCol={{ offset: 8 }}>
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
  const updateKeywords = (dry_run = false) => {
    return (keywords) => {
      return dispatch({
        type: 'keyword/updateKeywords',
        payload: {
          keywords: keywords.map(keyword => ({ name: keyword, aliases: [] })),
          dry_run,
        },
      })
    }
  }
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
    checkKeywords: updateKeywords(true),
    addKeywords: updateKeywords(),
  }
}

export default connect(props, actions)(Add)
