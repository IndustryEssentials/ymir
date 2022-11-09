import { TableColumnsType } from 'antd'

import Name from './columns/Name'
import Source from './columns/Source'
import Count from './columns/Count'
import Keywords from './columns/Keywords'
import State from './columns/State'
import CreateTime from './columns/CreateTime'
import Stages from './columns/Stages'
import InferModel from './columns/InferModel'
import InferDataset from './columns/InferDataset'
import InferConfig from './columns/InferConfig'

export function getInferDatasetColumns() {
  const inferDataset: TableColumnsType<YModels.InferDataset> = [InferModel(), InferDataset(), InferConfig(), State(), CreateTime()]
  return inferDataset
}
export function getDatasetColumns() {
  const columns: TableColumnsType<YModels.Dataset> = [Name(), Source(), Count(), Keywords(), State(), CreateTime()]
  return columns
}
export function getModelColumns() {
  const columns: TableColumnsType<YModels.Model> = [Name('model'), Stages(), Source(), State(), CreateTime()]
  return columns
}
