import { CheckboxOptionType, Radio } from 'antd'
import { FC } from 'react'
import { RadioChangeEvent } from 'antd/lib/radio'
import t from '@/utils/t'

type Props = {
  options?: CheckboxOptionType[]
  label?: string
  value?: string[]
  onChange?: (e: RadioChangeEvent) => void
  prefix?: string
}

const RadioGroup: FC<Props> = ({ options, value, onChange = () => {}, prefix = '', ...rest }) => {
  return <Radio.Group value={value} options={options?.map((opt) => ({ ...opt, label: t(`${prefix}${opt.label}`) }))} onChange={onChange} {...rest} />
}

export default RadioGroup
