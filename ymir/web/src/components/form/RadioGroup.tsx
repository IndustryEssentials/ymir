import { CheckboxOptionType, Radio } from 'antd'
import type { FC } from 'react'
import type { RadioGroupProps } from 'antd/lib/radio'
import t from '@/utils/t'
interface Props extends RadioGroupProps {
  options?: CheckboxOptionType[]
  prefix?: string
}

const RadioGroup: FC<Props> = ({ options = [], value, onChange = () => {}, prefix = '', ...rest }) => {
  return <Radio.Group value={value} options={options?.map((opt) => ({ ...opt, label: t(`${prefix}${opt.label}`) }))} onChange={onChange} {...rest} />
}

export default RadioGroup
