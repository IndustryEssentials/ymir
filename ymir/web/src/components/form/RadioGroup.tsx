import { CheckboxOptionType, Radio } from 'antd'
import type { FC, MouseEventHandler } from 'react'
import type { RadioChangeEventTarget, RadioGroupProps } from 'antd/lib/radio'
import t from '@/utils/t'
interface Props extends Omit<RadioGroupProps, 'optionType'> {
  options?: CheckboxOptionType[]
  prefix?: string
}

const RadioGroup: FC<Props> = ({ options = [], value, onChange = () => {}, prefix = '', ...rest }) => {
  const radioClick: MouseEventHandler = (ev) => {
    const target = ev.target as unknown as RadioChangeEventTarget
    if(target.value != value) {
      return
    }
    const newEv = {...ev, target: {
      ...ev.target,
      checked: false
    }}
    onChange(newEv)
  }
  return (
    <Radio.Group {...rest} value={value} onChange={onChange}>
      {options?.map(({ value, label }, index) => (
        <Radio.Button key={index} value={value} onClick={radioClick}>
          {t(`${prefix}${label}`)}
        </Radio.Button>
      ))}
    </Radio.Group>
  )
}

export default RadioGroup
