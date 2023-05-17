import React, { useEffect, useState } from 'react'
import { getRecommendStage, getStage } from '@/constants/model'
import VersionName from './VersionName'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'

type Props = { id?: number; result?: YModels.Model; stageId?: number }
const ModelVersionName: React.FC<Props> = ({ id, result, stageId }) => {
  const cache = useSelector(({ model }) => {
    return id ? model.model[id] : undefined
  })
  const { run: getModel } = useRequest<null, [{ id: number }]>('model/getModel')
  const [model, setModel] = useState<YModels.Model>()
  const [stage, setStage] = useState<YModels.Stage>()

  useEffect(() => {
    id && getModel({ id })
  }, [id])
  useEffect(() => {
    setModel(cache || result)
  }, [cache, result])
  useEffect(() => {
    model && stageId && setStage(getStage(model, stageId))
  }, [model])
  return model ? <VersionName result={model} extra={stage?.name} /> : null
}

export default ModelVersionName
