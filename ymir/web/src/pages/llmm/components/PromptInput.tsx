import { FC, useState, useEffect } from 'react'
import { useSelector } from 'umi'
import t from '@/utils/t'
import { Form, Input } from 'antd'
type Props = {}
const PromptInput: FC<Props> = ({}) => {
  const [text, setText] = useState<string>('')

  useEffect(() => {}, [])
  return (
    <Form.Item name="prompt" label={t('llmm.prompt.label')} required>
      <Input.TextArea maxLength={256} placeholder={t('llmm.prompt.placeholder')} />
    </Form.Item>
  )
}
export default PromptInput
