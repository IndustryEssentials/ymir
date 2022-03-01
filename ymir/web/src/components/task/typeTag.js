import { getDatasetTypes } from '@/constants/query'

const TypeTag = ({ types = getDatasetTypes(),  type, id, name }) => {

  
  const target = types.find((t) => t.value === type)
  if (!target) {
    return type
  }

  return target.label
}

export default TypeTag
