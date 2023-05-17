import { Select, SelectProps } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'
import { Types } from './AddTypes'
const types = [
  { id: Types.INTERNAL, label: 'internal' },
  { id: Types.COPY, label: 'copy' },
  { id: Types.NET, label: 'net' },
  { id: Types.LOCAL, label: 'local' },
  { id: Types.PATH, label: 'path' },
]
const TypeSelector: FC<Omit<SelectProps, 'options'>> = (props) => {
  const options = types.map((type) => ({
    value: type.id,
    label: t(`dataset.add.types.${type.label}`),
  }))
  return <Select defaultValue={Types.LOCAL} {...props} options={options} />
}

export default TypeSelector
