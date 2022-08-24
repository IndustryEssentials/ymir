import { Form } from "antd"
import RadioGroup from "@/components/form/radioGroup"
const options = [
  { value: 0, label: 'new' },
  { value: 1, label: 'exist' },
]
const MergeType = ({ initialValue = 0 }) => (
  <Form.Item name='type' {...{ initialValue }} label={'Merge Type'}>
    <RadioGroup options={options} labelPrefix='task.merge.type.' />
  </Form.Item>
)

export default MergeType
