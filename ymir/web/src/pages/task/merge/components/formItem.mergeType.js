import { Form } from "antd"
import RadioGroup from "@/components/form/radioGroup"
import t from '@/utils/t'

const options = [
  { value: 0, label: 'new' },
  { value: 1, label: 'exist' },
]
const MergeType = ({ initialValue = 0, disabled = [] }) => (
  <Form.Item name='type' initialValue={initialValue} label={t('task.merge.type.label')}>
    <RadioGroup
      options={options.map(option => ({
        ...option,
        disabled: disabled.includes(option.value)
      }))}
      labelPrefix='task.merge.type.'
    />
  </Form.Item>
)

export default MergeType
