import { Button, Card, Form, message, Space } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'
import { useParams, useHistory } from 'umi'

import { formLayout } from "@/config/antd"
import t from '@/utils/t'
import ModelSelect from "@/components/form/modelSelect"
import s from './add.less'
import Breadcrumbs from '@/components/common/breadcrumb'

const { useForm } = Form

const InitModel = ({ projects = {}, ...props }) => {
  const history = useHistory()
  const pageParams = useParams()
  const id = Number(pageParams.id)
  const [project, setProject] = useState({})

  const [form] = useForm()

  useEffect(() => {
    id && fetchProject()
  }, [id])

  useEffect(() => {
    if (projects[id]) {
      setProject(projects[id])
    }
  }, [projects[id]])

  useEffect(() => {
    initForm(project)
  }, [project])

  async function submit(values) {

    const params = {
      ...values,
      id,
    }
    const result = await props.updateProject(params)
    if (result) {
      message.success(t('project.initmodel.success.msg'))
      history.goBack()
    }
  }


  function initForm(project = {}) {
    const { model, modelStage } = project
    if (model) {
      form.setFieldsValue({
        modelStage,
      })
    }
  }

  function fetchProject() {
    props.getProject(id)
  }

  return (
    <div className={s.wrapper}>
      <Breadcrumbs />
      <Card className={s.container} title={t('project.iteration.initmodel')}>
        <div className={s.formContainer}>
          <Form
            name='datasetImportForm'
            className={s.form}
            {...formLayout}
            form={form}
            labelCol={{ span: 6, offset: 2 }}
            wrapperCol={{ span: 12 }}
            onFinish={submit}
            labelAlign={'left'}
            colon={false}
          >
            <Form.Item
              label={t('task.mining.form.model.label')}
              name="modelStage"
              rules={[
                { required: true, message: t('task.mining.form.model.required') },
              ]}
              tooltip={t('tip.iteration.initmodel')}
            >
              <ModelSelect placeholder={t('task.mining.form.mining.model.required')} pid={id} />
            </Form.Item>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.confirm')}
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

const props = state => ({
  projects: state.project.projects,
})

const actions = (dispatch) => {
  return {
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
  }
}

export default connect(props, actions)(InitModel)
