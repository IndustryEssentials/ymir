import React, { useEffect, useState } from 'react'
import { getRecommendStage, getStage } from '@/constants/model'
import VersionName from './VersionName'
import { useSelector } from 'umi'
import useFetch from '@/hooks/useFetch'

type Props = { id?: number; result?: YModels.Model; stageId?: number }
const ModelVersionName: React.FC<Props> = ({ id, result, stageId }) => {
  const cache = useSelector(({ model }: YStates.Root) => {
    return id && model.model[id]
  })
  const [_, getModel] = useFetch('model/getModel')
  const [model, setModel] = useState<YModels.Model>()

  useEffect(() => id && getModel({ id }), [id])
  useEffect(() => {
    setModel(cache || result)
  }, [cache, result])
  const stage: YModels.Stage | undefined = model ? (stageId ? getStage(model, stageId) : getRecommendStage(model)) : undefined
  const extra = stage?.name || ''
  return <VersionName result={model} extra={extra} />
}

export default ModelVersionName
