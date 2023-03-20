import { Form, Radio } from "antd"
import t from "@/utils/t"
import { getLabelAnnotationTypes } from '@/constants/common'


const KeepAnnotations = ({ initialValue, isPred = false, ...rest }) => {
  const prefix = 'task.label.form.keep_anno.'
  const options = getLabelAnnotationTypes(isPred)
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
