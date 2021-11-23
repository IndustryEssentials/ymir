import { useEffect, useState } from 'react'
import { Button, Form, Input, message, Modal, Select, Row, Col, Space, } from 'antd'
import { connect } from 'dva'

import s from './add.less'
import t from '@/utils/t'
import { AddDelTwoIcon, AddIcon, AddTwoIcon } from '../../components/common/icons'

const { Option } = Select
const { useForm } = Form

const Add = ({ visible, keys = [], cancel = () => { }, ok = () => { }, updateKeywords }) => {

  const [form] = useForm()
  const [show, setShow] = useState(visible)
  const [keywords, setKeywords] = useState([])

  useEffect(() => {
    setKeywords(keys)
    form.setFieldsValue({ keywords: keys.length ? keys : [{ name: '' }] })
  }, [keys])

  useEffect(() => {
    setShow(visible)
  }, [visible])

  const close = () => {
    setShow(false)
    cancel()
  }

  const onOk = async () => {

    if (form.validateFields()) {
      const { keywords } = form.getFieldsValue()
      const result = await updateKeywords(keywords.filter(k => k && k.name))
      if (result) {
        message.success(t('keyword.add.success'))
        form.resetFields()
        close()
        ok()
      } else {
        // todo
      }
    }
  }
  const onCancel = () => {
    close()
  }

  const repeatKeywords = (_, value) => {
    const kws = form.getFieldValue('keywords')
    const keys = []
    kws.forEach(k => {
      k && (
        k.name ? keys.push(k.name.trim()) : null,
        keys.push(...(k.aliases || []))
      )
    })
    if (keys.filter(k => k === (Array.isArray(value) ? value[value.length - 1] : value)).length > 1) {
      return Promise.reject(t('keyword.name.repeat'))
    }
    Promise.resolve()
  }

  const validChar = (_, value) => {
    const reg = /^[^\s\t\n,]+$/
    if (reg.test(value.trim())) {
      return Promise.resolve()
    }
    Promise.reject(t('keyword.add.name.validchar'))
  }

  return (
    <Modal
      visible={show}
      title={t('keyword.add.label')}
      onCancel={onCancel}
      onOk={onOk}
      width={680}
    >
      <Form name='keywordAddForm' form={form} layout='vertical'>
        <Form.List name='keywords'>
          {(fields, { add, remove }) => (
            <div className={s.content}>
              {fields.map(field => (
                <Row key={field.key} gutter={20} wrap={false}>
                  <Col flex={'40%'}>
                    <Form.Item
                      {...field}
                      label={field.name === 0 ? t('keyword.add.name.label') : null}
                      required={true}
                      // label="Key"
                      name={[field.name, 'name']}
                      fieldKey={[field.fieldKey, 'name']}
                      rules={[
                        { validator: validChar },
                        { validator: repeatKeywords }
                      ]}
                    >
                      <Input disabled={!!keys.length} allowClear maxLength={50} placeholder={t('keyword.add.name.placeholder')} />
                    </Form.Item>
                  </Col>
                  <Col flex={1}>
                    <Form.Item
                      {...field}
                      // label="Value"
                      label={field.name === 0 ? t('keyword.add.alias.label') : null}
                      name={[field.name, 'aliases']}
                      fieldKey={[field.fieldKey, 'aliases']}
                      rules={[
                        { validator: repeatKeywords }
                      ]}
                    >
                      <Select
                        mode='tags'
                        tokenSeparators={[',']}
                        placeholder={t('keyword.add.alias.placeholder')}
                      >
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col flex={'100px'} style={{ alignSelf: field.name ? '' : 'center' }}>
                    <Space>
                      {fields.length <= 1 ? null : <AddDelTwoIcon className={s.removeBtn} onClick={() => remove(field.name)} title={'remove the row'} />}
                      {!keys.length && (field.name === fields.length - 1) ? <AddTwoIcon className={s.addBtn} onClick={() => add()} title={'add a new row'} /> : null}
                    </Space>
                  </Col>
                </Row>
              ))}
            </div>
          )}
        </Form.List>
      </Form>
    </Modal>
  )
}


const actions = (dispatch) => {
  return {
    updateKeywords: (payload) => {
      return dispatch({
        type: 'keyword/updateKeywords',
        payload,
      })
    },
  }
}

export default connect(null, actions)(Add)
