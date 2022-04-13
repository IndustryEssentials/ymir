import { getTaskTypeLabel } from '@/constants/task'
import t from '@/utils/t'

const TypeTag = ({ type = 0 }) => {

  return t(getTaskTypeLabel(type))
}

export default TypeTag
