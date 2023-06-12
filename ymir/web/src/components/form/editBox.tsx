import { useState, useEffect, forwardRef, useImperativeHandle, FC, PropsWithChildren } from 'react'
import { Modal, Form, ModalFuncProps } from 'antd'
import t from '@/utils/t'
import { Group, Result } from '@/constants'

type Props = PropsWithChildren<
  Omit<ModalFuncProps, 'visible' | 'onOk'> & {
    record?: Group | Result
    update?: Function
  }
>

export type RefProps = {
  show: () => void
}

const { useForm } = Form
const EditBox = forwardRef<RefProps, Props>(({ children, record, update = () => {}, ...props }, ref) => {
  const [editForm] = useForm()
  const [show, setShow] = useState(false)

  useImperativeHandle(
    ref,
    () => ({
      show: () => {
        console.log('edit box show:', true)
        setShow(true)
      },
    }),
    [],
  )

  useEffect(() => {
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
    <Modal title={t('common.editbox.action.edit')} destroyOnClose forceRender onCancel={onCancel} {...props} visible={show} onOk={onOk}>
      <Form form={editForm} labelCol={{ span: 6 }} colon={false} labelAlign="left">
        {children}
      </Form>
    </Modal>
  )
})

export default EditBox
