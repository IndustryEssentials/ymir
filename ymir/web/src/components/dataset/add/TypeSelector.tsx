import { Select, SelectProps } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'
import { getTypeLabel, Types } from './AddTypes'
const types = [Types.LOCAL, Types.NET, Types.PATH, Types.COPY, Types.INTERNAL]
type OptionType = {
  label: string
  value: Types
}
const TypeSelector: FC<Omit<SelectProps<Types>, 'options'>> = (props) => {
  const options: OptionType[] = types.map((type) => ({
    value: type,
    label: t(getTypeLabel(type)),
  }))
  return <Select defaultValue={Types.LOCAL} {...props} options={options} />
}

export default TypeSelector
