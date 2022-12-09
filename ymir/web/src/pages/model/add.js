import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Upload } from 'antd'
import { useParams, connect, useHistory, useLocation } from 'umi'

import { formLayout } from "@/config/antd"
import t from '@/utils/t'
import { generateName } from '@/utils/string'
import useFetch from '@/hooks/useFetch'

import { urlValidator } from '@/components/form/validators'
import Breadcrumbs from '@/components/common/breadcrumb'
import ProjectSelect from "@/components/form/ProjectModelSelect"
import Desc from "@/components/form/desc"
import Uploader from '@/components/form/uploader'

import s from './add.less'

const { Option } = Select
const { useForm } = Form


const TYPES = Object.freeze({
  COPY: 1,
  LOCAL: 2,
  NET: 3,
})

// todo update tips for segmentation
const Add = () => {
  const types = [
    { id: TYPES.COPY, label: t('model.add.types.copy') },
    { id: TYPES.NET, label: t('model.add.types.net') },
    { id: TYPES.LOCAL, label: t('model.add.types.local') },
  ]

  const history = useHistory()
  const { query } = useLocation()
  const { mid, from, stepKey } = query
  const iterationContext = from === 'iteration'
  const { id: pid } = useParams()
  const [form] = useForm()
  const [path, setPath] = useState('')
  const [currentType, setCurrentType] = useState(mid ? TYPES.COPY : TYPES.LOCAL)
  const initialValues = {
    name: generateName('import_model'),
    modelId: Number(mid) ? [Number(pid), Number(mid)] : undefined,
  }
  const [importResult, importModel] = useFetch('model/importModel')
  const [updateResult, updateProject] = useFetch('project/updateProject')

  useEffect(() => {
    if (updateResult) {
      history.replace(`/home/project/${pid}/iterations`)
    }
  }, [updateResult])

  useEffect(() => {
    if (importResult) {
      message.success(t('model.add.success'))
      if (iterationContext && stepKey) {
        return updateProject({ id: pid, [stepKey]: [importResult.id] })
      }
      const group = importResult.model_group_id || ''
      history.push(`/home/project/${pid}/model#${group}`)
    }
  }, [importResult])

  function submit(values) {
    const params = {
      ...values,
      projectId: pid,
      url: (values.url || '').trim(),
    }
    if (isType(TYPES.LOCAL)) {
      if (path) {
        params.path = path
      } else {
        return message.error(t('model.file.required'))
      }
    }
    if (values.modelId) {
      params.modelId = values.modelId[values.modelId.length - 1]
    }
    importModel(params)
  }

  const typeChange = (type) => {
    setCurrentType(type)
  }

  function isType(type) {
    return currentType === type
  }
  return (
    <div className={s.wrapper}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.model.add')}>
        <div className={s.formContainer}>
          <Form form={form}
            {...formLayout}
            onFinish={submit} initialValues={initialValues}
          >
            <Form.Item
              label={t('model.add.form.name')}
              name='name'
              rules={[
                { required: true, whitespace: true, message: t('model.add.form.name.placeholder') },
                { type: 'string', min: 2, max: 80 },
              ]}
            >
              <Input placeholder={t('model.add.form.name.placeholder')} autoComplete='off' allowClear />
            </Form.Item>
            <Form.Item label={t('model.add.form.type')}>
              <Select onChange={(value) => typeChange(value)} defaultValue={TYPES.LOCAL}>
                {types.map(type => (
                  <Option value={type.id} key={type.id}>{type.label}</Option>
                ))}
              </Select>
            </Form.Item>
            {isType(TYPES.COPY) ?
              <Form.Item label={t('model.add.form.project')} name='modelId' rules={[
                { required: true, }
              ]}>
                <ProjectSelect pid={pid} />
              </Form.Item>
              : null}
            {isType(TYPES.LOCAL) ?
              <Form.Item label={t('model.add.form.upload.btn')} name='path' required>
                <Uploader
                  onChange={(files, result) => { setPath(result) }}
                  max={1024}
                  format='all'
                  onRemove={() => setPath('')}
                  info={t('model.add.form.upload.info', { br: <br />, max: 1024 })}
                ></Uploader>
              </Form.Item>
              : null}

            {isType(TYPES.NET) ?
              <Form.Item
                label={t('model.add.form.url')}
                name='url'
                rules={[
                  { required: true, message: t('model.add.form.url.tip') },
                  { validator: urlValidator, }
                ]}
                extra={t('model.add.form.url.help')}
              >
                <Input placeholder={t('model.add.form.url.placeholder')} max={512} allowClear />
              </Form.Item>
              : null}
            <Desc form={form} />
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.action.import')}
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

export default Add
