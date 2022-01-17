import { Modal, Form, Input, message } from "antd"
import { useEffect, useState, forwardRef, useImperativeHandle } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import { phoneValidate } from "@/components/form/validators"

const { useForm } = Form
const ShareModal = forwardRef(({ username, email, phone, ok = () => {}, shareImage }, ref) => {
  const [shareForm] = useForm()
  const [visible, setVisible] = useState(false)
  const [id, setId] = useState(null)
  const [imageName, setImageName] = useState('')

  useEffect(() => {
    shareForm.setFieldsValue({ email, phone })
  }, [email, phone ])

  useImperativeHandle(ref, () => ({
    show: (id, name) => {
      setVisible(true)
      shareForm.setFieldsValue({ email, phone })
      setId(id)
      setImageName(name)
    }
  }), [])

  const shareModalCancel = () => setVisible(false)

  const submitShare = () => {
    shareForm.validateFields().then(async ({ org, ...other }) => {
      const params = {
        username,
        id,
        ...other,
        org: (org || '').trim(),
      }
      const result = await shareImage(params)
      if (result) {
        message.success(t('image.share.success'))
        setVisible(false)
        ok()
      }
    })
  }

  return <Modal visible={visible} onCancel={shareModalCancel} onOk={submitShare} destroyOnClose title={t('image.share.title', {name: imageName})}>
  <Form
    form={shareForm}
    name='shareForm'
    labelAlign='left'
    size='large'
    preserve={false}
  >

    {/* <Form.Item label={t("signup.username")}> {username} </Form.Item> */}
    <Form.Item
      label={t("signup.email")}
      name="email"
      rules={[
        { required: true, message: t("signup.email.required.msg"), },
        { type: "email", message: t("signup.email.format.msg"), },
      ]}
    >
      <Input allowClear placeholder={t('signup.email.placeholder')} />
    </Form.Item>
    <Form.Item
      label={t("signup.phone")}
      name="phone"
      rules={[{ validator: phoneValidate }]}
    >
      <Input allowClear placeholder={t('signup.phone.placeholder')} />
    </Form.Item>
    <Form.Item
      label={t("image.share.org")}
      name="org"
      rules={[{ max: 100 }]}
    >
      <Input allowClear placeholder={t('image.share.org.placeholder')} />
    </Form.Item>
  </Form>
</Modal>
})

const props = (state) => {
  return {
    username: state.user.username,
    phone: state.user.phone,
    email: state.user.email,
  }
}
const actions = (dispatch) => {
  return {
    shareImage(payload) {
      return dispatch({
        type: 'image/shareImage',
        payload,
      })
    }
  }
}
export default connect(props, actions, null, { forwardRef: true })(ShareModal)
