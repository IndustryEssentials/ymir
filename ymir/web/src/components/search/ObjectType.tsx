import { Select, SelectProps } from 'antd'
import { FC } from 'react'

import t from '@/utils/t'
import { getProjectTypes } from '@/constants/project'

const types = getProjectTypes()

const ObjectType: FC<SelectProps> = (props) => {
  const options = types.map((item) => ({
    ...item,
    label: t(item.label),
  }))
  return <Select {...props} options={options} style={{ width: 200 }} placeholder={t('common.object.type')} allowClear></Select>
}

export default ObjectType
