import Name from './columns/Name'
import Source from './columns/Source'
import Count from './columns/Count'
import Keywords from './columns/Keywords'
import State from './columns/State'
import CreateTime from './columns/CreateTime'
import Stages from './columns/Stages'

type Type = 'dataset' | 'model' | 'inferDataset'

const getColumns = (type: Type) => {
  const maps = {
    dataset: [Name(), Source, Count, Keywords, State, CreateTime],
    model: [Name('model'), Stages, Source, State, CreateTime],
    inferDataset: [State, CreateTime],
  }
  return maps[type]
}

export default getColumns
