import { Modal, Form, Input, Select, message } from "antd"
import { forwardRef, useEffect, useState, useImperativeHandle } from "react"
import { connect } from 'dva'

import t from '@/utils/t'

const { useForm } = Form
const MultiAdd = forwardRef(({ addKeywords, ok = () => { } }, ref) => {
  const [visible, setVisible] = useState(false)
  const [form] = useForm()

  useImperativeHandle(ref, () => ({
    show: () => {
      setVisible(true)
    }
  }), [])

  const cancel = () => setVisible(false)

  const submit = () => {
    form.validateFields().then(async () => {
      const keywords = transKeywords(form.getFieldValue('keywords'))
      const result = await addKeywords(keywords)
      if (result) {
        if (result.failed && !result.failed.length) {
          message.success(t('keyword.multiadd.success'))
          setVisible(false)
          form.resetFields()
          ok()
        } else {
          message.error(t('keyword.name.repeat'))
          setRepeats(result.failed || [])
        }
      } else {
        message.error(t('keyword.add.failure'))
      }
    })
  }

  function transKeywords(text) {
    let keywords = []
    try {
      keywords = text.split(/\s*\n\s*/).map(line => {
        const pair = line.trim().split(/\s*:\s*/)
        let aliases = []
        if (pair[1]) {
          aliases = pair[1].trim().split(/\s*,\s*/).filter(alias => !!alias)
        }
        if (pair[0]) {
          return {
            name: pair[0].replace(',', ''),
            aliases,
          }
        }
      }).filter((name) => name)
    } catch (e) {
      message.error(t('keyword.multiadd.invalid'))
    }
    return keywords
  }

  return <Modal visible={visible} onCancel={cancel} onOk={submit} destroyOnClose title={t('keyword.multiadd.title')}>
    <Form
      form={form}
      name='multiAddForm'
      labelAlign='left'
      preserve={false}
    >
      <Form.Item
        name="keywords"
        label={t('keyword.multiadd.kws.label')}
        rules={[
          { required: true }
        ]}
        help={t('keyword.multiadd.kws.placeholder')}
      >
        <Input.TextArea allowClear placeholder={t('keyword.multiadd.kws.placeholder')} autoSize={{ minRows: 6, maxRows: 10 }}>
        </Input.TextArea>
      </Form.Item>
    </Form>
  </Modal>
})

const props = (state) => {
  return {
    username: state.user.username,
  }
}
const actions = (dispatch) => {
  return {
    addKeywords: (keywords) => {
      return dispatch({
        type: 'keyword/updateKeywords',
        payload: { keywords },
      })
    },
  }
}
export default connect(props, actions, null, { forwardRef: true })(MultiAdd)
