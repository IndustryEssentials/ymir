import { Form, Input } from "antd"
import t from '@/utils/t'

const DatasetName = ({
  name = 'name',
  itemProps = {},
  inputProps = {},
  prefix = 'dataset.add.form.name',
}) => {
  const rules = [
    { required: true, whitespace: true, message: t(`${prefix}.required`) },
    { type: 'string', min: 2, max: 80 },
  ]
  return <Form.Item
    {...itemProps}
    label={t(`${prefix}.label`)}
    name={name}
    rules={rules}
  >
    <Input autoComplete={'off'} placeholder={t(`${prefix}.placeholder`)} {...inputProps} allowClear />
  </Form.Item>
}

export default DatasetName
