import { Form, Radio } from "antd"
import t from "@/utils/t"
import { getLabelAnnotationTypes } from '@/constants/common'

const options = getLabelAnnotationTypes()

const KeepAnnotations = ({ initialValue, ...rest }) => {
  const prefix = 'task.label.form.keep_anno.'
  return <Form.Item name='keepAnnotations'
    required
    label={t(`${prefix}label`)}
    initialValue={initialValue}
    {...rest}
  >
    <Radio.Group options={options.map(opt => ({ ...opt, label: t(opt.label) }))} />
  </Form.Item>
}

export default KeepAnnotations
