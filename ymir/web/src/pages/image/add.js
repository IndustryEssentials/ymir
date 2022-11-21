import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Space } from 'antd'
import { useParams, useHistory, useLocation } from 'umi'

import s from './add.less'
import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import { formLayout } from '@/config/antd'
import Breadcrumbs from '@/components/common/breadcrumb'

const { useForm } = Form

const Add = () => {
  const { id } = useParams()
  const history = useHistory()
  const location = useLocation()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const [userInput, setUserInput] = useState(false)
  const [image, getImage, setImage] = useFetch('image/getImage')
  const [created, createImage] = useFetch('image/createImage')
  const [updated, updateImage] = useFetch('image/updateImage')

  useEffect(() => {
    setEdit(!!id)

    id && getImage({ id })
  }, [id])

  useEffect(() => {
    if (created || updated) {
      const msg = created ? 'image.add.success' : 'image.update.success'
      message.success(t(msg))
      history.push('/home/image')
    }
  }, [created, updated])

  useEffect(() => {
    if (!location.state) {
      return
    }
    const record = location.state.record
    console.log('record:', record)
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
    image?.name && initForm(image)
  }, [image])

  function initForm(image = {}) {
    const { name, url, description } = image
    if (name) {
      form.setFieldsValue({
        name,
        url,
        description,
      })
    }
  }

  const submit = (values) => {
    isEdit ? update(values) : create(values)
  }

  const checkImageUrl = (_, value) => {
    const reg = /^[^\s]+$/
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

  function create({ url, name, description }) {
    var params = {
      url: url.trim(),
      name: name.trim(),
      description: (description || '').trim(),
    }
    createImage(params)
  }

  function update({ name, description }) {
    var params = {
      id,
      name: name.trim(),
      description: (description || '').trim(),
    }
    updateImage(params)
  }

  return (
    <div className={s.imageAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.image.add')}>
        <div className={s.formContainer}>
          <Form form={form} {...formLayout} labelAlign="left" onFinish={submit}>
            <Form.Item
              label={t('image.add.form.url')}
              tooltip={t('tip.image.add.name')}
              name="url"
              rules={[{ required: true, message: t('image.add.form.url.required') }, { validator: checkImageUrl }]}
            >
              <Input placeholder={t('image.add.form.url.placeholder')} disabled={image?.url} autoComplete="off" allowClear onChange={urlChange} />
            </Form.Item>
            <Form.Item
              label={t('image.add.form.name')}
              tooltip={t('tip.image.add.url')}
              name="name"
              rules={[{ required: true, whitespace: true, message: t('image.add.form.name.placeholder') }, { max: 50 }]}
            >
              <Input placeholder={t('image.add.form.name.placeholder')} maxLength={50} autoComplete="off" allowClear onKeyUp={() => setUserInput(true)} />
            </Form.Item>
            <Form.Item label={t('image.add.form.desc')} name="description" tooltip={t('tip.image.add.desc')} rules={[{ max: 500 }]}>
              <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
            </Form.Item>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name="submitBtn" noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {isEdit ? t('image.update.submit') : t('image.add.submit')}
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
