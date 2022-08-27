import { Radio } from "antd"
import t from '@/utils/t'

const RadioGroup = ({ value, onChange = () => { }, options, labelPrefix = '' }) => (
  <Radio.Group
    options={options.map(item => ({ ...item, label: t(`${labelPrefix}${item.label}`) }))}
    value={value}
    onChange={onChange}
  ></Radio.Group>
)

export default RadioGroup
