import { FC } from 'react'
import t from '@/utils/t'
import { getProjectTypeLabel, ObjectType } from '@/constants/objectType'

type Props = {
  type: ObjectType
}

const ObjectTypeTag: FC<Props> = ({ type }) => {
  const cls = getProjectTypeLabel(type)
  const label = getProjectTypeLabel(type, true)

  return <span className={`extraTag ${cls}`}>{t(label)}</span>
}

export default ObjectTypeTag
