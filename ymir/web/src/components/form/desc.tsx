import { FC } from 'react'
import { Form, Input } from 'antd'
import t from '@/utils/t'

const Desc: FC<{ label?: string; name?: string }> = ({ label = 'common.desc', name = 'description' }) => {
  return (
    <Form.Item label={t(label)} name={name} rules={[{ max: 500 }]}>
      <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
    </Form.Item>
  )
}

export default Desc
