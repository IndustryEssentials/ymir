import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import RenderProgress from '@/components/common/Progress'

function State<T extends YModels.AllResult>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.state" />,
    dataIndex: 'state',
    render: (state, record) => RenderProgress(state, record),
  }
}

export default State
