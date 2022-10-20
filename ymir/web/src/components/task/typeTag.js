import { getTaskTypeLabel } from '@/constants/task'
import t from '@/utils/t'

const TypeTag = ({ type }) => {
  return type ? t(getTaskTypeLabel(type)) : null
}

export default TypeTag
