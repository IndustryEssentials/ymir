import { getTaskTypeLabel } from '@/constants/task'

const TypeTag = ({ type = 0 }) => {

  return getTaskTypeLabel(type)
}

export default TypeTag
