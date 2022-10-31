import Name from './columns/Name'
import Source from './columns/Source'
import Count from './columns/Count'
import Keywords from './columns/Keywords'
import State from './columns/State'
import CreateTime from './columns/CreateTime'
import Stages from './columns/Stages'
import { TableColumnsType } from 'antd'
import { Result } from '@/interface/common'

type Type = 'inferDataset'

function getColumns<T extends Result> (type: Type) {
  const inferDataset: TableColumnsType<T> = [State<T>(), CreateTime<T>()]
  const maps = {
    // dataset: [Name(), Source, Count, Keywords, State<T>(), CreateTime<T>()],
    // model: [Name('model'), Stages, Source, State<T>(), CreateTime<T>()],
    inferDataset,
  }
  return maps[type]
}

export default getColumns
