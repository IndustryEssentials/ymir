import { FC } from 'react'
import t from '@/utils/t'
import { Form, Input } from 'antd'
type Props = {}
const max = 255
const PromptInput: FC<Props> = ({}) => (
  <Form.Item name="prompt" label={t('llmm.prompt.label')} rules={[{ required: true }, { max }]}>
    <Input.TextArea maxLength={max} placeholder={t('llmm.prompt.placeholder')} showCount />
  </Form.Item>
)

export default PromptInput
