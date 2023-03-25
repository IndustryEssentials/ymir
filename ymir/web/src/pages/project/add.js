import { useEffect, useCallback, useState } from 'react'
import { Button, Card, Form, Input, message, Space, Radio } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory, useLocation } from 'umi'

import s from './add.less'
import t from '@/utils/t'
import { HIDDENMODULES } from '@/constants/common'
import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetSelect from '@/components/form/datasetSelect'
import Panel from '@/components/form/panel'
import useFetch from '@/hooks/useFetch'
import ProjectTypes from '@/components/project/ProjectTypes'

const { useForm } = Form

const Add = (func) => {
  const { id } = useParams()
  const history = useHistory()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const [project, getProject] = useFetch('project/getProject', {})

  useEffect(() => {
    setEdit(!!id)

    id && getProject({ id })
  }, [id])

  useEffect(() => {
    initForm(project)
  }, [project])

  function initForm(project = {}) {
    const { name, type, description, enableIteration, testingSets } = project
    if (name) {
      form.setFieldsValue({
        name,
        type,
        description,
        enableIteration,
        testingSets: testingSets.length ? testingSets : undefined,
      })
    }
  }

  const submit = async ({ name = '', description = '', ...values }) => {
    const action = isEdit ? 'update' : 'create'
    var params = {
      ...values,
    }
    if (isEdit) {
      params.id = id
    }
    params.name = (name || '').trim()
    params.description = (description || '').trim()

    if (isEdit && params.name === project.name) {
      delete params.name
    }

    const result = await func[`${action}Project`](params)
    if (result) {
      const pid = result.id || id
      message.success(t(`project.${action}.success`))
      history.push(`/home/project/${pid}/dataset`)
    }
  }

  const testingFilter = useCallback((datasets) => datasets.filter((ds) => ds.keywordCount > 0 && ds.groupId !== project?.trainSet?.id), [project?.trainSet?.id])

  const renderTitle = t(`breadcrumbs.project.${isEdit ? 'edit' : 'add'}`)

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={renderTitle}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ offset: 2, span: 6 }} wrapperCol={{ span: 12 }} colon={false} labelAlign="left" onFinish={submit} scrollToFirstError>
            <Panel hasHeader={false}>
              <Form.Item
                label={t('project.add.form.name')}
                name="name"
                rules={[
                  { required: true, whitespace: true, message: t('project.add.form.name.required') },
                  { min: 1, max: 100 },
                ]}
              >
                <Input placeholder={t('project.add.form.name.placeholder')} autoComplete="off" allowClear />
              </Form.Item>
              <ProjectTypes disabled={isEdit} />
              <Form.Item
                label={t('project.add.form.enableIteration')}
                name="enableIteration"
                hidden={HIDDENMODULES.ITERATIONSWITCH}
                initialValue={HIDDENMODULES.ITERATIONSWITCH}
                required
                tooltip={t('project.add.form.enableIteration.tip')}
              >
                <Radio.Group
                  disabled={isEdit}
                  options={[
                    { value: true, label: t('common.yes') },
                    { value: false, label: t('common.no') },
                  ]}
                />
              </Form.Item>
              {isEdit ? (
                <Form.Item label={t('project.add.form.testing.set')} name="testingSets" tooltip={t('project.add.form.testingset.tip')}>
                  <DatasetSelect pid={id} mode="multiple" filters={testingFilter} allowClear />
                </Form.Item>
              ) : null}
              <Form.Item label={t('project.add.form.desc')} name="description" rules={[{ max: 500 }]}>
                <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
              </Form.Item>
            </Panel>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name="submitBtn" noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {isEdit ? t('common.confirm') : t('project.add.submit')}
                  </Button>
                </Form.Item>
                <Form.Item name="backBtn" noStyle>
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
    }
  }
}

export default connect(null, actions)(Add)
