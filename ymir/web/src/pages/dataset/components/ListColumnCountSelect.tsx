import { Select, SelectProps } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'

const ListColumnCountSelect: FC<SelectProps> = ({ value, ...props }) => {
  const options = [3, 5, 10].map((value) => ({
    value,
    label: t('dataset.assets.selector.columns.label', { count: value }),
  }))
  return <Select {...props} value={value} options={options} />
}

export default ListColumnCountSelect
