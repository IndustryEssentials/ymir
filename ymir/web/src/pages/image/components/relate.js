import { Modal, Form, Input, Select, message } from "antd"
import { forwardRef, useEffect, useState, useImperativeHandle } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import { TYPES, STATES } from '@/constants/image'
import useFetch from '@/hooks/useFetch'

const { useForm } = Form
const RelateModal = forwardRef(({ ok = () => { } }, ref) => {
  const [visible, setVisible] = useState(false)
  const [links, setLinks] = useState([])
  const [id, setId] = useState(null)
  const [imageName, setImageName] = useState('')
  const [linkForm] = useForm()
  const [relateResult, relate] = useFetch('image/relateImage')
  const [{ items: images }, getMiningImages] = useFetch('image/getImages', { items: [] })

  useEffect(() => linkForm.setFieldsValue({
    relations: links.map(image => image.id)
  }), [links, visible])

  useEffect(() => visible && getMiningImages({
    type: TYPES.MINING,
    offset: 0,
    limit: 10000,
  }), [visible])

  useEffect(() => {
    if (relateResult) {
      message.success(t('image.link.success'))
      setVisible(false)
      ok()
    }
  }, [relateResult])

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
    linkForm.validateFields().then(() => {
      const { relations } = linkForm.getFieldValue()
      relate({ id, relations })
    })
  }

  return <Modal
    visible={visible}
    onCancel={linkModalCancel}
    onOk={submitLink}
    destroyOnClose
    forceRender
    title={t('image.link.title')}
  >
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

export default RelateModal
