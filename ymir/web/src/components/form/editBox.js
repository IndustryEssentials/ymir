import { useState, useEffect } from "react"
import { Modal, Form, Input } from "antd"
import t from '@/utils/t'

const { useForm } = Form
const EditBox = ({ children, record, max=50, action = () => { } }) => {
  const [editForm] = useForm()
  const [show, setShow] = useState(false)
  const { id, name, type, state } = record

  useEffect(() => {
    setShow(!!id)
    editForm.setFieldsValue({ name })
  }, [id])

  function onOk() {
    editForm.validateFields().then((values) => {
      const fname = values.name.trim()
      if (name === fname) {
        return
      }
      action(record, fname)
      setShow(false)
    })
  }
  function onCancel() {
    setShow(false)
  }
  return <Modal
    visible={show}
    title={t('common.editbox.action.edit')}
    onCancel={onCancel}
    onOk={onOk}
    destroyOnClose
  >
    <Form form={editForm} labelCol={{ span: 6 }} colon={false} labelAlign='left'>
      <Form.Item
        label={t('common.editbox.name')}
        name='name'
        initialValue={name}
        rules={[
          { required: true, whitespace: true, message: t('common.editbox.form.name.required') },
          { type: 'string', min: 2, max },
        ]}
      >
        <Input placeholder={t('common.editbox.form.name.placeholder')} autoComplete={'off'} allowClear />
      </Form.Item>
      {children}
    </Form>
  </Modal>
}

export default EditBox
