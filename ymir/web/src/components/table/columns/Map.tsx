import { ColumnType } from 'antd/lib/table'

import { percent } from '@/utils/number'
import StrongTitle from './StrongTitle'
import { getStage } from '@/constants/model'
import { Prediction } from '@/constants'

function Map<T extends Prediction>(label = 'model.stage.metrics.primary.label.det'): ColumnType<T> {
  return {
    title: <StrongTitle label={label} />,
    dataIndex: 'map',
    render: (_, { inferModel, inferModelId }) => {
      if (!inferModel) {
        return null
      }
      const stage = getStage(inferModel, inferModelId[1])
      return stage?.primaryMetric ? percent(stage.primaryMetric) : null
    },
    width: 120,
  }
}

export default Map
