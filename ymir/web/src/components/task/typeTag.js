import { Link } from 'umi'
import { TASKTYPES } from '../../constants/task'
import { getDatasetTypes } from '@/constants/query'
import t from '@/utils/t'

const TypeTag = ({ types = getDatasetTypes(),  type, id, name }) => {

  
  const target = types.find((t) => t.value === type)
  if (!target) {
    return type
  }

  return [TASKTYPES.TRAINING, TASKTYPES.LABEL, TASKTYPES.MINING, TASKTYPES.FILTER].indexOf(target.value) > -1 ? (
    <>
      {t(`dataset.action.${target.key}`)}: 
      <Link to={`/home/task/detail/${id}`}>{name}</Link>
    </>
  ) : target.label
}

export default TypeTag
