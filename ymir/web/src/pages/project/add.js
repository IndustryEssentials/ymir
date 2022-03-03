import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Radio } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory, useLocation } from "umi"

import s from './add.less'
import t from '@/utils/t'
import Breadcrumbs from '@/components/common/breadcrumb'
import Tip from '@/components/form/tip'

const { useForm } = Form

const Add = ({ getProject, createProject, updateProject }) => {
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
    if (!location.state) {
      return
    }
    const record = location.state.record
    if (!record?.docker_name) {
      return
    }
    const { docker_name, description, organization, contributor } = record
    const project = {
      name: docker_name,
      url: docker_name,
      description: `${description}\n---------\nOrg.: ${organization}\nContributor: ${contributor}`,
    }
    setProject(project)
  }, [location.state])

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

  const checkProjectUrl = (_, value) => {
    const reg = /^([a-zA-Z0-9]{4,30}\/)?[a-z0-9]+(?:[._-][a-z0-9]+)*(:[a-zA-Z0-9._-]+)?$/
    if (!value || reg.test(value.trim())) {
      return Promise.resolve()
    }
    return Promise.reject(t('project.add.form.url.invalid'))
  }
  const urlChange = ({ target }) => {
    const name = form.getFieldValue('name')
    if (!userInput) {
      form.setFieldsValue({ name: target.value })
    }
  }
  async function fetchProject() {
    const result = await getProject(id)
    if (result) {
      setProject(result)
    }
  }

  async function create({ url, name, description }) {
    var params = {
      url: url.trim(),
      name: name.trim(),
      description: (description || '').trim(),
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

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.project.add')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 4 }} onFinish={submit}>
            <Tip content={t('tip.project.add.name')}>
              <Form.Item
                label={t('project.add.form.url')}
                name='url'
                rules={[
                  { required: true, message: t('project.add.form.url.required') },
                  { validator: checkProjectUrl },
                ]}
              >
                <Input placeholder={t('project.add.form.url.placeholder')} disabled={project.url} autoComplete='off' allowClear onChange={urlChange} />
              </Form.Item>
            </Tip>
            <Tip content={t('tip.project.add.url')}>
              <Form.Item
                label={t('project.add.form.name')}
                name='name'
                rules={[
                  { required: true, whitespace: true, message: t('project.add.form.name.placeholder') },
                  { max: 50 },
                ]}
              >
                <Input placeholder={t('project.add.form.name.placeholder')} maxLength={50}
                  autoComplete='off' allowClear onKeyUp={() => setUserInput(true)} />
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
  }
}

export default connect(null, actions)(Add)
