import { Radio } from "antd"
import t from '@/utils/t'

const RadioGroup = ({ value, onChange = () => { }, options, labelPrefix = '', ...props }) => (
  <Radio.Group
    options={options.map(item => ({ ...item, label: t(`${labelPrefix}${item.label}`) }))}
    value={value}
    onChange={onChange}
    {...props}
  ></Radio.Group>
)

export default RadioGroup
