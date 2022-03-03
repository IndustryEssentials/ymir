import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Radio, Row, Col, InputNumber } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory, useLocation } from "umi"

import s from './add.less'
import t from '@/utils/t'
import Breadcrumbs from '@/components/common/breadcrumb'
import Tip from '@/components/form/tip'

const { useForm } = Form

const Add = ({ keywords, datasets, getProject, createProject, updateProject, getKeywords }) => {
  const { id } = useParams()
  const history = useHistory()
  const location = useLocation()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const [userInput, setUserInput] = useState(false)
  const [project, setProject] = useState({ id })

  useEffect(() => {
    setEdit(!!id)

    id && fetchProject()
  }, [id])

  useEffect(() => {
    getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    initForm(project)
  }, [project])

  function initForm(project = {}) {
    const { name, url, description } = project
    if (name) {
      form.setFieldsValue({
        name, url, description,
      })
    }
  }

  const submit = (values) => {
    isEdit ? update(values) : create(values)
  }

  const checkProjectName = (_, value) => {
    const reg = /^[a-z0-9]+(?:[._-][a-z0-9]+)*(:[a-zA-Z0-9._-]+)?$/
    if (!value || reg.test(value.trim())) {
      return Promise.resolve()
    }
    return Promise.reject(t('project.add.form.name.invalid'))
  }

  async function fetchProject() {
    const result = await getProject(id)
    if (result) {
      setProject(result)
    }
  }

  async function create({ name, description, ...values }) {
    console.log('hello create project: ', name, description, values)
    var params = {
      name: name.trim(),
      description: (description || '').trim(),
      ...values,
    }
    const result = await createProject(params)
    if (result) {
      message.success(t('project.add.success'))
      history.push('/home/project')
    }
  }

  async function update({ name, description }) {
    var params = {
      id,
      name: name.trim(),
      description: (description || '').trim(),
    }
    const result = await updateProject(params)
    if (result) {
      message.success(t('project.update.success'))
      history.push('/home/project')
    }
  }

  const renderSetSelect = (sets = []) => <Select showArrow
    placeholder={t('project.add.form.trainset.placeholder')}>
    {sets.map(set => (
      <Option key={set.name} value={set.id}>{set.name}</Option>
    ))}
  </Select>

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.project.add')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 4 }} onFinish={submit} scrollToFirstError>
            <Tip content={t('tip.project.add.name')}>
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
            <Tip content={t('tip.project.add.type')}>
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
            <Tip content={t('tip.project.add.keyword')}>
              <Form.Item
                label={t('project.add.form.keyword.label')}
                name="keywords"
                rules={[
                  { required: true, message: t('project.add.form.keyword.required') }
                ]}
              >
                <Select mode="multiple" showArrow
                  placeholder={t('project.add.form.keyword.placeholder')} 
                  filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}>
                  {keywords.map(keyword => (
                    <Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                      <Row>
                        <Col flex={1}>{keyword.name}</Col>
                      </Row>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Tip>
            <Tip content={t('tip.project.add.target')}>
              <Form.Item label={t('project.add.form.target')}>
                <div className={s.targetPanel}>
                  <Form.Item labelCol={{ span: 3 }} colon={false} labelAlign='left' label={t('project.add.form.target.map')} name='map'>
                    <InputNumber min={0} max={100} step={1} formatter={value => `${value}%`} parser={value => value.replace('%', '')} style={{ width: '100%' }} placeholder={t('project.add.form.target.map.placeholder')} allowClear />
                  </Form.Item>
                  <Form.Item labelCol={{ span: 3 }} colon={false} labelAlign='left' label={t('project.add.form.target.interations')} name='interations'>
                    <InputNumber min={1} step={1} placeholder={t('project.add.form.target.interations.placeholder')} style={{ width: '100%' }} allowClear />
                  </Form.Item>
                  <Form.Item labelCol={{ span: 3 }} colon={false} labelAlign='left' label={t('project.add.form.target.dataset')} name='dataset'>
                    <InputNumber min={1} step={1} placeholder={t('project.add.form.target.dataset.placeholder')} style={{ width: '100%' }} allowClear />
                  </Form.Item>
                </div>
              </Form.Item>
            </Tip>
            <Tip content={t('tip.project.add.desc')}>
              <Form.Item label={t('project.add.form.desc')} name='description'
                rules={[
                  { max: 500 },
                ]}
              >
                <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
              </Form.Item>
            </Tip>
            <div className={s.interationSettings} hidden={true}>
              <h3>{t('project.interation.settings.title')}</h3>
              <Tip content={t('tip.project.add.trainset')}>
                <Form.Item
                  label={t('project.add.form.keyword.label')}
                  name="train_set"
                >
                  {renderSetSelect(datasets)}
                </Form.Item>
              </Tip>
            </div>
            <Tip hidden={true}>
              <Form.Item wrapperCol={{ offset: 4 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit">
                      {isEdit ? t('project.update.submit') : t('project.add.submit')}
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
        payload: id,
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
