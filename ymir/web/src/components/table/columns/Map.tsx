import { ColumnType } from 'antd/lib/table'
import { useSelector } from 'umi'

import { percent } from '@/utils/number'
import StrongTitle from './StrongTitle'
import { getStage } from '@/constants/model'

function Map<T extends YModels.InferDataset>(): ColumnType<T> {
  const models = useSelector(({ model }: YStates.Root) => {
    return model.model
  })
  return {
    title: <StrongTitle label="model.column.map" />,
    dataIndex: 'map',
    render: (_, { inferModel, inferModelId }) => {
      if (!inferModel) {
        return null
      }
      const stage = getStage(inferModel, inferModelId[1])
      return stage?.map ? percent(stage.map) : null
    },
    width: 120,
  }
}

export default Map
