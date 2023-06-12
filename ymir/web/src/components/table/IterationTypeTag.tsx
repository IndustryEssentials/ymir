import { FC, useState, useEffect } from 'react'
import t from '@/utils/t'
import { Project } from '@/constants'
type Props = {
  project?: Project
  gid?: number
  id?: number
  model?: boolean
}
type Maps = {
  [id: number]: {
    type: Types
    v?: string
  }
}

enum Types {
  isTrainSet = 'project.tag.train',
  isTestSet = 'project.tag.test',
  isMiningSet = 'project.tag.mining',
  isTestingSet = 'project.tag.testing',
  isInitModel = 'project.tag.model',
}

const extraTag = {
  padding: '2px 8px',
  fontSize: '12px',
  color: 'rgba(0, 0, 0, 0.65)',
  backgroundColor: '#f5f5f5',
}

const setId = (type: Types, id?: number, version?: string) => (id ? { [id]: { type, v: version } } : {})

const IterationTypeTag: FC<Props> = ({ project, gid, id, model }) => {
  const [label, setLabel] = useState<string>('')
  const [typesById, setTypesById] = useState<Maps>({})
  const [typesByGroup, setTypeByGroup] = useState<Maps>({})

  useEffect(() => {
    if (!project) {
      return
    }
    if (model) {
      return setTypesById(setId(Types.isInitModel, project.model))
    }
    const tid: Maps = {
      ...setId(Types.isTestSet, project.testSet?.id),
      ...setId(Types.isMiningSet, project.miningSet?.id),
      ...project.testingSets?.reduce((prev, ds) => ({ ...prev, [ds]: Types.isTestingSet }), {}),
    }

    const tgid: Maps = {
      ...setId(Types.isTrainSet, project.trainSet?.id),
      ...setId(Types.isTestSet, project.testSet?.groupId, project.testSet?.versionName),
      ...setId(Types.isMiningSet, project.miningSet?.groupId, project.miningSet?.versionName),
    }
    setTypesById(tid)
    setTypeByGroup(tgid)
  }, [project, model])

  useEffect(() => {
    if (!id) {
      return
    }
    typesById[id] && setLabel(t(typesById[id].type, { version: '' }))
  }, [typesById, id])

  useEffect(() => {
    if (!gid) {
      return
    }
    typesByGroup[gid] && setLabel(t(typesByGroup[gid].type, { version: typesByGroup[gid].v }))
  }, [typesByGroup, gid])

  return label ? <span style={extraTag}>{label}</span> : null
}
export default IterationTypeTag
