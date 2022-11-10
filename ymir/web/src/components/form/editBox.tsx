import { useState, useEffect, ComponentProps, ReactComponentElement, ReactChildren } from 'react'
import { Modal, Form, Input } from 'antd'
import t from '@/utils/t'

interface Props {
  record: YModels.Group | YModels.Result
  update?: Function
}

const { useForm } = Form
const EditBox: React.FC<Props> = ({ children, record, update = () => {} }) => {
  const [editForm] = useForm()
  const [show, setShow] = useState(false)
  const { id } = record

  useEffect(() => {
    setShow(!!id)
    editForm.setFieldsValue(record)
  }, [record])

  function onOk() {
    editForm.validateFields().then((values) => {
      update(record, values)
      setShow(false)
    })
  }
  function onCancel() {
    setShow(false)
  }
  return (
    <Modal visible={show} title={t('common.editbox.action.edit')} onCancel={onCancel} onOk={onOk} destroyOnClose forceRender>
      <Form form={editForm} labelCol={{ span: 6 }} colon={false} labelAlign="left">
        {children}
      </Form>
    </Modal>
  )
}

export default EditBox
