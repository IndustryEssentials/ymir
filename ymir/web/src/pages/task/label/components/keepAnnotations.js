import { Form, Radio } from "antd"
import t from "@/utils/t"

const options = [
  { value: 1, label: 'gt' },
  { value: 2, label: 'pred' },
  { value: undefined, label: 'none' },
]

const KeepAnnotations = ({ initialValue, ...rest }) => {
  const prefix = 'task.label.form.keep_anno.'
  return <Form.Item name='keepAnnotations'
    required
    label={t(`${prefix}label`)}
    initialValue={initialValue}
    {...rest}
  >
    <Radio.Group options={options.map(opt => ({ ...opt, label: t(prefix + opt.label) }))} />
  </Form.Item>
}

export default KeepAnnotations
