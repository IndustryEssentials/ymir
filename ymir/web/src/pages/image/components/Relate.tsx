import { Modal, Form, Select, message } from 'antd'
import { forwardRef, useEffect, useState, useImperativeHandle } from 'react'

import t from '@/utils/t'
import { TYPES } from '@/constants/image'
import useRequest from '@/hooks/useRequest'
import { Image } from '@/constants'
import { List } from '@/models/typings/common'
import { QueryParams } from '@/services/typings/image'

export type RefProps = {
  show: (img: Pick<Image, 'id' | 'related' | 'name'>) => void
}
type Props = {
  ok?: () => void
}
const { useForm } = Form
const RelateModal = forwardRef<RefProps, Props>(({ ok = () => {} }, ref) => {
  const [visible, setVisible] = useState(false)
  const [links, setLinks] = useState<Image[]>([])
  const [id, setId] = useState<number>()
  const [imageName, setImageName] = useState('')
  const [linkForm] = useForm()
  const { data: relateResult, run: relate } = useRequest<Image, [{ id: number; relations: number[] }]>('image/relateImage')
  const { data: { items: images } = {}, run: getMiningImages } = useRequest<List<Image>, [QueryParams]>('image/getImages', { loading: false })

  useEffect(
    () =>
      linkForm.setFieldsValue({
        relations: links.map((image) => image.id),
      }),
    [links, visible],
  )

  useEffect(() => {
    visible &&
      getMiningImages({
        type: TYPES.MINING,
        offset: 0,
        limit: 10000,
      })
  }, [visible])

  useEffect(() => {
    if (relateResult) {
      message.success(t('image.link.success'))
      setVisible(false)
      ok()
    }
  }, [relateResult])

  useImperativeHandle(
    ref,
    () => ({
      show: ({ id, name, related }) => {
        setVisible(true)
        setId(id)
        setImageName(name)
        setLinks(related || [])
      },
    }),
    [],
  )

  const linkModalCancel = () => setVisible(false)

  const submitLink = () => {
    linkForm.validateFields().then(() => {
      const { relations } = linkForm.getFieldsValue()
      id && relations?.length && relate({ id, relations })
    })
  }

  return (
    <Modal visible={visible} onCancel={linkModalCancel} onOk={submitLink} destroyOnClose forceRender title={t('image.link.title')}>
      <Form form={linkForm} name="linkForm" labelAlign="left" size="large" preserve={false}>
        <Form.Item label={t('image.link.name')}>{imageName}</Form.Item>
        <Form.Item name="relations" label={t('image.links.title')}>
          <Select
            allowClear
            placeholder={t('image.links.placeholder')}
            mode="multiple"
            optionFilterProp="label"
            options={images?.map((image) => ({ value: image.id, label: image.name }))}
          ></Select>
        </Form.Item>
      </Form>
    </Modal>
  )
})

export default RelateModal
