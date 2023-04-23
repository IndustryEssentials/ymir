import { Form, Input } from 'antd'
import t from '@/utils/t'

import EditBox, { RefProps } from './editBox'
import useFetch from '@/hooks/useFetch'
import { forwardRef, Ref, useEffect } from 'react'

interface Props {
  record?: YModels.Group
  type?: string
  max?: number
  handle?: Function
}

const EditNameBox = forwardRef<RefProps, Props>(({ type = 'dataset', record, max = 50, handle, children }, ref) => {
  const func = type === 'dataset' ? 'updateDataset' : 'updateModelGroup'
  const [updated, updateResult] = useFetch(`${type}/${func}`)
  const name = record?.name || ''

  useEffect(() => handle && handle(updated), [updated])

  function update(record: YModels.Group, values: any) {
    const fname = values.name.trim()
    if (name === fname) {
      return
    }
    updateResult({ id: record.id, name: fname })
  }

  return (
    <EditBox ref={ref} record={record} update={update}>
      <Form.Item
        label={t('common.editbox.name')}
        name="name"
        initialValue={name}
        rules={[
          { required: true, whitespace: true, message: t('common.editbox.form.name.required') },
          { type: 'string', min: 2, max },
        ]}
      >
        <Input placeholder={t('common.editbox.form.name.placeholder')} autoComplete={'off'} allowClear />
      </Form.Item>
      {children}
    </EditBox>
  )
})

export default EditNameBox
