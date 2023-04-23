import { TableColumnsType } from 'antd'

import { ObjectType } from '@/constants/project'

import Name from './columns/Name'
import Source from './columns/Source'
import Count from './columns/Count'
import Keywords from './columns/Keywords'
import State from './columns/State'
import CreateTime from './columns/CreateTime'
import Stages from './columns/Stages'
import Map from './columns/Map'
import InferModel from './columns/InferModel'
import InferDataset from './columns/InferDataset'
import InferConfig from './columns/InferConfig'
import { getPrimaryMetricsLabel } from '@/constants/model'
import Image from './columns/Image'
import { Prediction } from '@/constants'

export function getPredictionColumns(type: ObjectType): TableColumnsType<Prediction> {
  const label = type ? getPrimaryMetricsLabel(type) : undefined
  return [InferModel(), InferDataset(), InferConfig(), Image(), State(), CreateTime(false)]
}
export function getDatasetColumns(): TableColumnsType<YModels.Dataset>  {
  return [Name(), Source(), Count(), Keywords(), State(), CreateTime()]
}
export function getModelColumns(): TableColumnsType<YModels.Model> {
  return [Name('model'), Stages(), Source(), State(), CreateTime()]
}
