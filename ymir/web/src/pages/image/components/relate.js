import { Modal, Form, Input, Select, message } from "antd"
import { forwardRef, useEffect, useState, useImperativeHandle } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import { TYPES, STATES } from '@/constants/image'

const { useForm } = Form
const RelateModal = forwardRef(({ getMiningImage, relate, ok = () => { } }, ref) => {
  const [visible, setVisible] = useState(false)
  const [links, setLinks] = useState([])
  const [images, setImages] = useState([])
  const [id, setId] = useState(null)
  const [imageName, setImageName] = useState('')
  const [linkForm] = useForm()

  useEffect(() => {
    linkForm.setFieldsValue({ relations: links.map(image => image.id) })
  }, [links, visible])

  useEffect(() => {
    visible && fetchMiningImages()
  }, [visible])

  useImperativeHandle(ref, () => ({
    show: ({ id, name, related }) => {
      setVisible(true)
      setId(id)
      setImageName(name)
      setLinks(related)
    }
  }), [])

  const linkModalCancel = () => setVisible(false)

  const submitLink = () => {
    linkForm.validateFields().then(async () => {
      const { relations } = linkForm.getFieldValue()
      const result = await relate(id, relations)
      if (result) {
        message.success(t('image.link.success'))
        setVisible(false)
        ok()
      }
    })
  }

  async function fetchMiningImages() {
    const result = await getMiningImage()
    if (result) {
      setImages(result.items)
    }
  }

  return <Modal visible={visible} onCancel={linkModalCancel} onOk={submitLink} destroyOnClose title={t('image.link.title')}>
    <Form
      form={linkForm}
      name='linkForm'
      labelAlign='left'
      size='large'
      preserve={false}
    >
      <Form.Item label={t('image.link.name')}>{imageName}</Form.Item>
      <Form.Item
        name="relations"
        label={t('image.links.title')}
      >
        <Select allowClear placeholder={t('image.links.placeholder')}
          mode="multiple" optionFilterProp='label' options={images.map(image => ({ value: image.id, label: image.name }))}>
        </Select>
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
    getImageRelated(id) {
      return dispatch({
        type: 'image/getImageRelated',
        payload: id,
      })
    },
    relate(id, relations) {
      return dispatch({
        type: 'image/relateImage',
        payload: { id, relations },
      })
    },
    getMiningImage() {
      return dispatch({
        type: 'image/getImages',
        payload: { type: TYPES.MINING, offset: 0, limit: 10000, },
      })
    }
  }
}
export default connect(props, actions, null, { forwardRef: true })(RelateModal)
