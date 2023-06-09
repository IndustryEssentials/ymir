import { useEffect, useCallback, useState, FC } from 'react'
import { Button, Card, Form, Input, message, Space, Radio } from 'antd'
import { useParams, useHistory } from 'umi'

import s from './add.less'
import t from '@/utils/t'
import { HIDDENMODULES } from '@/constants/common'
import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetSelect from '@/components/form/datasetSelect'
import Panel from '@/components/form/panel'
import ProjectTypes from '@/components/project/ProjectTypes'
import useRequest from '@/hooks/useRequest'
import { Dataset, Project, Task } from '@/constants'
import { Image } from '@/services/typings/image.d'
import { CreateParams, UpdateParams } from '@/services/project'
import LLMM from '@/constants/llmm'
import { isMultiModal } from '@/constants/objectType'

const { useForm } = Form

const Add: FC = () => {
  const { id } = useParams<{ id: string }>()
  const pid = Number(id)
  const history = useHistory()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const { data: project, run: getProject } = useRequest<Project, [{ id: number }]>('project/getProject', {
    loading: false,
  })
  const { data: created, run: createProject } = useRequest<Project, [CreateParams]>('project/createProject')
  const { data: updated, run: updateProject } = useRequest<Project, [UpdateParams]>('project/updateProject')
  const { data: pulling, run: createLLMMImage } = useRequest<Task>('image/createLLMMImage', {
    loading: false,
  })

  useEffect(() => {
    setEdit(!!pid)

    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    project && initForm(project)
  }, [project])

  useEffect(() => {
    if (created || updated) {
      const pid = created?.id || id
      message.success({ content: t(`project.${isEdit ? 'update' : 'create'}.success`), key: 'success' })
      history.push(`/home/project/${pid}/dataset`)
    }
    if (created && isMultiModal(created.type)) {
      createLLMMImage()
    }
  }, [created, updated])

  useEffect(() => {
    pulling && message.success({ content: t('llmm.image.add.tip'), key: 'success' })
  }, [pulling])

  function initForm(project: Project) {
    const { name, type, description, enableIteration, testingSets } = project
    if (name) {
      form.setFieldsValue({
        name,
        type,
        description,
        enableIteration,
        testingSets: testingSets?.length ? testingSets : undefined,
      })
    }
  }

  const submit = ({ name = '', description = '', ...values }) => {
    const params = {
      ...values,
    }
    if (isEdit) {
      params.id = id
    }
    params.name = (name || '').trim()
    params.description = (description || '').trim()

    if (isEdit && params.name === project?.name) {
      delete params.name
    }

    isEdit ? updateProject(params) : createProject(params as CreateParams)
  }

  const testingFilter = useCallback(
    (datasets: Dataset[]) => datasets.filter((ds) => ds.keywordCount > 0 && ds.groupId !== project?.trainSet?.id),
    [project?.trainSet?.id],
  )

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
                  <DatasetSelect pid={pid} mode="multiple" filters={testingFilter} allowClear />
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

export default Add
