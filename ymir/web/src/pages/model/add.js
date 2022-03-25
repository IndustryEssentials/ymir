import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Upload } from 'antd'
import { useParams, connect, useHistory } from 'umi'

import t from '@/utils/t'
import { generateName } from '@/utils/string'
import Breadcrumbs from '@/components/common/breadcrumb'
import Tip from "@/components/form/tip"
import ModelSelect from "@/components/form/modelSelect"
import ProjectSelect from "@/components/form/projectSelect"
import Uploader from '@/components/form/uploader'
import s from './add.less'

const { Option } = Select
const { useForm } = Form


const TYPES = Object.freeze({
  COPY: 1,
  LOCAL: 2,
})

const Add = ({ importModel }) => {
  const types = [
    { id: TYPES.COPY, label: t('model.add.types.share') },
    { id: TYPES.LOCAL, label: t('model.add.types.local') },
  ]

  const history = useHistory()
  const { pid } = useParams()
  const [form] = useForm()
  const [url, setUrl] = useState('/ymir-storage/472ee37fe649efa355c1d12152191f24.ymir')
  const [currentType, setCurrentType] = useState(TYPES.LOCAL)
  const initialValues = {
    name: generateName('import_model'),
  }

  async function submit(values) {
    console.log('values:', values)
    var params = {
      ...values,
      projectId: pid,
      url,
    }
    const result = await importModel(params)
    if (result) {
      message.success(t('model.add.success'))
    }
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
          <Form form={form} labelCol={{ span: 4 }} onFinish={submit} initialValues={initialValues}>
            <Tip hidden={true}>
              <Form.Item
                label={t('model.add.form.name')}
                name='name'
                rules={[
                  { required: true, message: t('model.add.form.name.placeholder') }
                ]}
              >
                <Input placeholder={t('model.add.form.name.placeholder')} autoComplete='off' allowClear />
              </Form.Item>
            </Tip>
            <Tip hidden={true}>
              <Form.Item label={t('model.add.form.type')}>
                <Select onChange={(value) => typeChange(value)} defaultValue={TYPES.LOCAL}>
                  {types.map(type => (
                    <Option value={type.id} key={type.id}>{type.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Tip>
            {isType(TYPES.COPY) ?
              <>
                <Form.Item label={t('model.add.form.project')} name='project'>
                  <ProjectSelect />
                </Form.Item>
                <Form.Item label={t('model.add.form.model')}>
                  <ModelSelect />
                </Form.Item>
              </>
              : null}
            {isType(TYPES.LOCAL) ?
              <Tip hidden={true}>
                <Form.Item label={t('model.add.form.upload.btn')} name='url'>
                  <Uploader
                    onChange={(files, result) => { setUrl(result) }}
                    max={1024}
                    format='all'
                    onRemove={() => setUrl('')}
                    info={t('model.add.form.upload.info', { br: <br />, max: 1024 })}
                  ></Uploader>
                </Form.Item>
              </Tip> : null}

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
              <Form.Item wrapperCol={{ offset: 8 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit">
                      {t('task.create')}
                    </Button>
                  </Form.Item>
                  <Form.Item name='backBtn' noStyle>
                    <Button size="large" onClick={() => history.goBack()}>
                      {t('task.btn.back')}
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
    importModel: (payload) => {
      return dispatch({
        type: 'model/importModel',
        payload,
      })
    },
  }
}

export default connect(null, actions)(Add)
