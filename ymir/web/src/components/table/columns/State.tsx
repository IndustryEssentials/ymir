import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import RenderProgress from '@/components/common/Progress'
import { Dataset, Model, Prediction, Result } from '@/constants'

function State<T extends Dataset | Model | Prediction>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.state" />,
    dataIndex: 'state',
    render: (state, record) => RenderProgress(state, record),
  }
}

export default State
