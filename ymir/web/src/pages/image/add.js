import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Radio } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory, useLocation } from "umi"

import s from './add.less'
import t from '@/utils/t'
import Breadcrumbs from '@/components/common/breadcrumb'
import Tip from '@/components/form/tip'

const { useForm } = Form

const Add = ({ getImage, createImage, updateImage }) => {
  const { id } = useParams()
  const history = useHistory()
  const location = useLocation()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const [userInput, setUserInput] = useState(false)
  const [image, setImage] = useState({ id })

  useEffect(() => {
    setEdit(!!id)

    id && fetchImage()
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
    const image = {
      name: docker_name,
      url: docker_name,
      description: `${description}\n---------\nOrg.: ${organization}\nContributor: ${contributor}`,
    }
    setImage(image)
  }, [location.state])

  useEffect(() => {
    initForm(image)
  }, [image])

  function initForm(image = {}) {
    const { name, url, description } = image
    if (name) {
      form.setFieldsValue({
        name, url, description,
      })
    }
  }

  const submit = (values) => {
    isEdit ? update(values) : create(values)
  }

  const checkImageUrl = (_, value) => {
    const reg = /^([a-zA-Z0-9]{4,30}\/)?[a-z0-9]+(?:[._-][a-z0-9]+)*(:[a-zA-Z0-9._-]+)?$/
    if (!value || reg.test(value.trim())) {
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
  async function fetchImage() {
    const result = await getImage(id)
    if (result) {
      setImage(result)
    }
  }

  async function create({ url, name, description }) {
    var params = {
      url: url.trim(),
      name: name.trim(),
      description: (description || '').trim(),
    }
    const result = await createImage(params)
    if (result) {
      message.success(t('image.add.success'))
      history.push('/home/image')
    }
  }

  async function update({ name, description }) {
    var params = {
      id,
      name: name.trim(),
      description: (description || '').trim(),
    }
    const result = await updateImage(params)
    if (result) {
      message.success(t('image.update.success'))
      history.push('/home/image')
    }
  }

  return (
    <div className={s.imageAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.image.add')}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ span: 6, offset: 2 }} labelAlign='left' onFinish={submit}>
            <Tip content={t('tip.image.add.name')}>
              <Form.Item
                label={t('image.add.form.url')}
                name='url'
                rules={[
                  { required: true, message: t('image.add.form.url.required') },
                  { validator: checkImageUrl },
                ]}
              >
                <Input placeholder={t('image.add.form.url.placeholder')} disabled={image.url} autoComplete='off' allowClear onChange={urlChange} />
              </Form.Item>
            </Tip>
            <Tip content={t('tip.image.add.url')}>
              <Form.Item
                label={t('image.add.form.name')}
                name='name'
                rules={[
                  { required: true, whitespace: true, message: t('image.add.form.name.placeholder') },
                  { max: 50 },
                ]}
              >
                <Input placeholder={t('image.add.form.name.placeholder')} maxLength={50}
                  autoComplete='off' allowClear onKeyUp={() => setUserInput(true)} />
              </Form.Item>
            </Tip>
            <Tip content={t('tip.image.add.desc')}>
              <Form.Item label={t('image.add.form.desc')} name='description'
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
                      {isEdit ? t('image.update.submit') : t('image.add.submit')}
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
    createImage: (payload) => {
      return dispatch({
        type: 'image/createImage',
        payload,
      })
    },
    updateImage: (payload) => {
      return dispatch({
        type: 'image/updateImage',
        payload,
      })
    },
    getImage: (id) => {
      return dispatch({
        type: 'image/getImage',
        payload: id,
      })
    },
  }
}

export default connect(null, actions)(Add)
