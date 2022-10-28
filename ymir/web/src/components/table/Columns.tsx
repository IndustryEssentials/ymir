import Name from './columns/Name'
import Source from './columns/Source'
import Count from './columns/Count'
import Keywords from './columns/Keywords'
import State from './columns/State'
import CreateTime from './columns/CreateTime'
import Stages from './columns/Stages'
import { Dataset, InferDataset } from '@/interface/dataset'
import { ModelVersion } from '@/interface/model'
import { TableColumnsType } from 'antd'

type Type = 'dataset' | 'model' | 'inferDataset'
type ResultType = Dataset | ModelVersion | InferDataset

const getColumns = (type: Type) => {
  const inferDataset: TableColumnsType<ResultType> = [State, CreateTime]
  const maps = {
    dataset: [Name(), Source, Count, Keywords, State, CreateTime],
    model: [Name('model'), Stages, Source, State, CreateTime],
    inferDataset: [State, CreateTime],
  }
  return maps[type]
}

export default getColumns
