import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Radio } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory } from "umi"

import s from './add.less'
import t from '@/utils/t'
import { getImageTypeLabel } from '@/constants/image'
import Breadcrumbs from '../../components/common/breadcrumb'

const { useForm } = Form

const Add = ({ }) => {
  const { id } = useParams()
  const history = useHistory()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const [userInput, setUserInput] = useState(false)

  const types = Object.keys(getImageTypeLabel()).map(value => ({ value, label: getImageTypeLabel(value) }))

  useEffect(() => {
    setEdit(!!id)
  }, [id])

  const submit = async (values) => {
    var params = {
      ...values,
    }
    const result = await createImage(params)
    if (result) {
      message.success(t('image.add.success'))
      form.resetFields()
      close()
      ok()
    }
  }

  const checkImageUrl = (_, value) => {
    const reg = /^[a-z0-9\-._]{1,256}(:[a-z0-9.-_]+)?$/
    if (!value || reg.test(value)) {
      return Promise.resolve()
    }
    return Promise.reject(t('image.add.form.url.invalid'))
  }
  const urlChange = ({ target }) => {
    const name = form.getFieldValue('name')
    if (!userInput) {
      form.setFieldsValue({ name: target.value })
    }
  }
  return (
    <div className={s.imageAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.dataset.add')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 4 }} onFinish={submit}>
            <Form.Item
              label={t('image.add.form.url')}
              name='url'
              rules={[
                { required: true, message: t('image.add.form.url.required') },
                { validator: checkImageUrl },
              ]}
            >
              <Input placeholder={t('image.add.form.url.placeholder')} autoComplete='off' allowClear onChange={urlChange} />
            </Form.Item>
            <Form.Item
              label={t('image.add.form.name')}
              name='name'
              rules={[
                { required: true, message: t('image.add.form.name.placeholder') }
              ]}
            >
              <Input placeholder={t('image.add.form.name.placeholder')} autoComplete='off' allowClear onKeyUp={() => setUserInput(true)} />
            </Form.Item>
            <Form.Item
              label={t('image.add.form.share.label')}
              name='input_image_id'
              rules={[
                { required: true, message: t('image.add.form.share.valid.msg') }
              ]}
            >
              <Input placeholder={t('image.add.form.share.placeholder')} allowClear />
            </Form.Item>
            <Form.Item label={t('image.add.form.type')} name='type' initialValue={types[0].value}>
              <Radio.Group
                options={types}
              />
            </Form.Item>
            <Form.Item wrapperCol={{ offset: 4 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('image.add.submit')}
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


const actions = (dispatch) => {
  return {
    createImage: (payload) => {
      return dispatch({
        type: 'image/createImage',
        payload,
      })
    },
  }
}

export default connect(null, actions)(Add)
