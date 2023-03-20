import { Form, Input } from 'antd'
import t from '@/utils/t'

import EditBox from './editBox'
import useFetch from '@/hooks/useFetch'
import { useEffect } from 'react'

interface Props {
  record: YModels.Group
  type?: string
  max?: number
  handle?: Function
}

const EditNameBox: React.FC<Props> = ({ type = 'dataset', record, max = 50, handle, children }) => {
  const func = type === 'dataset' ? 'updateDataset' : 'updateModelGroup'
  const [updated, updateResult] = useFetch(`${type}/${func}`)
  const { name } = record

  useEffect(() => handle && handle(updated), [updated])

  function update(record: YModels.Group, values: any) {
    const fname = values.name.trim()
    if (name === fname) {
      return
    }
    updateResult({ id: record.id, name: fname })
  }

  return (
    <EditBox record={record} update={update}>
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
}

export default EditNameBox
