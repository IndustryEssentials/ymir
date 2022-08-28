import { Form } from "antd"
import RadioGroup from "@/components/form/radioGroup"
import t from '@/utils/t'

const options = [
  { value: 2, label: 'latest' },
  { value: 3, label: 'original' },
  { value: 1, label: 'terminate' },
]

const Strategy = ({ initialValue = 2, hidden = true, ...rest }) => {
  const prefix = 'task.train.form.repeatdata.'
  return <Form.Item name='strategy'
    hidden={hidden}
    initialValue={initialValue}
    label={t(`${prefix}label`)}
    {...rest}
  >
    <RadioGroup options={options} labelPrefix={prefix} />
  </Form.Item>
}

export default Strategy
