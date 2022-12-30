import { Select, SelectProps } from 'antd'
import { FC } from 'react'

import t from '@/utils/t'
import { getProjectTypes } from '@/constants/project'

const types = getProjectTypes()
const defaultAll = { label: t('common.all'), value: -1 }

const ObjectType: FC<SelectProps> = (props) => {
  const options = [
    defaultAll,
    ...types.map((item) => ({
      ...item,
      label: t(item.label),
    })),
  ]
  return <Select defaultValue={-1} {...props} options={options} style={{ width: 200 }}></Select>
}

export default ObjectType
