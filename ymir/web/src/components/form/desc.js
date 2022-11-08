import { Form, Input } from "antd"
import t from '@/utils/t'

export default function Desc({ label='common.desc', name = 'description' }) {
  return <Form.Item label={t(label)} name={name}
    rules={[
      { max: 500 },
    ]}
  >
    <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
  </Form.Item>
}
