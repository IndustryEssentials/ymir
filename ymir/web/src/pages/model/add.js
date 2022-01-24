import { useEffect, useState } from 'react'
import { Button, Form, Input, message, Modal, Select, Upload } from 'antd'
import { connect } from 'dva'
import {
  CloudUploadOutlined,
} from "@ant-design/icons"

import s from './add.less'
import t from '@/utils/t'
import Uploader from '@/components/form/uploader'

const { Option } = Select
const { useForm } = Form

const TYPES = Object.freeze({
  SHARE: 1,
  LOCAL: 2,
})

const Add = ({ visible, cancel = () => { }, ok = () => { }, createModel }) => {

  const types = [
    { id: TYPES.SHARE, label: t('model.add.types.share') },
    // { id: TYPES.LOCAL, label: t('model.add.types.local') },
  ]
  const [form] = useForm()
  const [show, setShow] = useState(visible)
  const [currentType, setCurrentType] = useState(TYPES.SHARE)
  const [fileToken, setFileToken] = useState('')

  useEffect(() => {
    setShow(visible)
  }, [visible])

  const typeChange = (type) => {
    setCurrentType(type)
  }

  const isType = (type) => {
    return currentType === type
  }

  const close = () => {
    setShow(false)
    cancel()
  }

  const onOk = async () => {

    if (form.validateFields()) {
      const values = form.getFieldsValue()
      var params = {
        ...values,
      }
      if (fileToken) {
        params.input_url = fileToken
      }
      const result = await createModel(params)
      if (result) {
        message.success(t('model.add.success'))
        form.resetFields()
        close()
        ok()
      }
    }
  }
  const onCancel = () => {
    close()
  }
  return (
    <Modal
      visible={show}
      title={t('model.import.label')}
      onCancel={onCancel}
      onOk={onOk}
    >
      <Form form={form} labelCol={{ span: 4 }}>
        <Form.Item
          label={t('model.add.form.name')}
          name='name'
          rules={[
            { required: true, message: t('model.add.form.name.placeholder') }
          ]}
        >
          <Input placeholder={t('model.add.form.name.placeholder')} autoComplete='off' allowClear />
        </Form.Item>
        <Form.Item label={t('model.add.form.type')}>
          <Select onChange={(value) => typeChange(value)} defaultValue={TYPES.SHARE}>
            {types.map(type => (
              <Option value={type.id} key={type.id}>{type.label}</Option>
            ))}
          </Select>
        </Form.Item>
        {isType(TYPES.SHARE) ? (
          <Form.Item
            label={t('model.add.form.share.label')}
            name='input_model_id'
            rules={[
              { required: true, message: t('model.add.form.share.valid.msg') }
            ]}
          >
            <Input placeholder={t('model.add.form.share.placeholder')} allowClear />
          </Form.Item>
        ) : null}
        {isType(TYPES.LOCAL) ? (
          <Form.Item label={t('model.add.form.upload.btn')}>
            <Uploader
              onChange={(files, result) => { setFileToken(result) }}
              info={t('model.add.form.upload.info', { br: <br /> })}
            ></Uploader>
          </Form.Item>
        ) : null}
      </Form>
    </Modal>
  )
}


const actions = (dispatch) => {
  return {
    createModel: (payload) => {
      return dispatch({
        type: 'model/createModel',
        payload,
      })
    },
  }
}

export default connect(null, actions)(Add)
