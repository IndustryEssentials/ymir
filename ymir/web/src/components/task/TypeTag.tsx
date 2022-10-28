import React from 'react'
import { getTaskTypeLabel, TASKTYPES } from '@/constants/task'
import t from '@/utils/t'

type Props = {
  type: TASKTYPES
}

const TypeTag: React.FC<Props> = ({ type }) => {
  return Boolean(type) ? t(getTaskTypeLabel(type)) : null
}

export default TypeTag
