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

export function getPredictionColumns(type: ObjectType): TableColumnsType<YModels.Prediction> {
  const label = type ? getPrimaryMetricsLabel(type) : undefined
  return [InferModel(), InferDataset(), InferConfig(), Map(label), State(), CreateTime(false)]
}
export function getDatasetColumns(): TableColumnsType<YModels.Dataset>  {
  return [Name(), Source(), Count(), Keywords(), State(), CreateTime()]
}
export function getModelColumns(): TableColumnsType<YModels.Model> {
  return [Name('model'), Stages(), Source(), State(), CreateTime()]
}
