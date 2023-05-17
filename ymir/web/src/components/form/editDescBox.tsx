import { Form, Input } from 'antd'
import t from '@/utils/t'

import EditBox, { RefProps } from './editBox'
import useFetch from '@/hooks/useFetch'
import { forwardRef, useEffect } from 'react'

interface Props {
  record?: YModels.Result
  type?: string
  max?: number
  handle?: Function
}

const EditDescBox = forwardRef<RefProps, Props>(({ type = 'dataset', record, max = 500, handle, children }, ref) => {
  const [updated, updateResult] = useFetch(`${type}/updateVersion`)
  const description = record?.description || ''

  useEffect(() => handle && handle(updated), [updated])

  function update(record: YModels.Result, values: any) {
    const desc = values.description.trim()
    if (description === desc) {
      return
    }
    updateResult({ id: record.id, description: desc })
  }

  return (
    <EditBox ref={ref} record={record} update={update}>
      <Form.Item label={t('common.editbox.desc')} name="description" initialValue={description} rules={[{ type: 'string', min: 2, max }]}>
        <Input placeholder={t('common.editbox.form.desc.placeholder')} autoComplete={'off'} allowClear />
      </Form.Item>
      {children}
    </EditBox>
  )
})

export default EditDescBox
