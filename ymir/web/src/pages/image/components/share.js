import { Modal, Form, Input, message } from 'antd'
import { useEffect, useState, forwardRef, useImperativeHandle } from 'react'
import { useSelector } from 'umi'

import t from '@/utils/t'
import { phoneValidate } from '@/components/form/validators'
import useFetch from '@/hooks/useFetch'

const { useForm } = Form
const ShareModal = forwardRef(({ ok = () => {} }, ref) => {
  const [shareForm] = useForm()
  const [visible, setVisible] = useState(false)
  const [id, setId] = useState(null)
  const [imageName, setImageName] = useState('')
  const { username, email, phone } = useSelector(({ user }) => user)
  const [shareResult, shareImage] = useFetch('image/shareImage')

  useEffect(() => {
    shareForm.setFieldsValue({ email, phone })
  }, [email, phone])

  useEffect(() => {
    if (shareResult) {
      message.success(t('image.publish.success'))
      setVisible(false)
      ok()
    }
  }, [shareResult])

  useImperativeHandle(
    ref,
    () => ({
      show: (id, name) => {
        setVisible(true)
        shareForm.setFieldsValue({ email, phone })
        setId(id)
        setImageName(name)
      },
    }),
    [],
  )

  const shareModalCancel = () => setVisible(false)

  const submitShare = () => {
    shareForm.validateFields().then(async ({ org, ...other }) => {
      const params = {
        username,
        id,
        ...other,
        org: (org || '').trim(),
      }
      shareImage(params)
    })
  }

  return (
    <Modal visible={visible} onCancel={shareModalCancel} onOk={submitShare} destroyOnClose title={t('image.publish.title', { name: imageName })} forceRender>
      <Form form={shareForm} name="shareForm" labelAlign="left" preserve={false}>
        <Form.Item
          label={t('signup.email')}
          name="email"
          rules={[
            { required: true, message: t('signup.email.required.msg') },
            { type: 'email', message: t('signup.email.format.msg') },
          ]}
        >
          <Input allowClear placeholder={t('signup.email.placeholder')} />
        </Form.Item>
        <Form.Item label={t('signup.phone')} name="phone" rules={[{ validator: phoneValidate }]}>
          <Input allowClear placeholder={t('signup.phone.placeholder')} />
        </Form.Item>
        <Form.Item label={t('image.publish.org')} name="org" rules={[{ max: 100 }]}>
          <Input allowClear placeholder={t('image.publish.org.placeholder')} />
        </Form.Item>
      </Form>
    </Modal>
  )
})

export default ShareModal
