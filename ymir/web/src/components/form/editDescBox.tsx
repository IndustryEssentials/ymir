import { Form, Input } from 'antd'
import t from '@/utils/t'

import EditBox from './editBox'
import useFetch from '@/hooks/useFetch'
import { useEffect } from 'react'

interface Props {
  record: YModels.Result
  type?: string
  max?: number
  handle?: Function
}

const EditDescBox: React.FC<Props> = ({ type = 'dataset', record, max = 500, handle, children }) => {
  const [updated, updateResult] = useFetch(`${type}/updateVersion`)
  const { description } = record

  useEffect(() => handle && handle(updated), [updated])

  function update(record: YModels.Result, values: any) {
    const desc = values.description.trim()
    if (description === desc) {
      return
    }
    updateResult({ id: record.id, description: desc })
  }

  return (
    <EditBox record={record} update={update}>
      <Form.Item label={t('common.editbox.desc')} name="description" initialValue={description} rules={[{ type: 'string', min: 2, max }]}>
        <Input placeholder={t('common.editbox.form.desc.placeholder')} autoComplete={'off'} allowClear />
      </Form.Item>
      {children}
    </EditBox>
  )
}

export default EditDescBox
