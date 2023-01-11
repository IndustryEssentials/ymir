import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import TypeTag from '@/components/task/TypeTag'

function Source<T extends YModels.Result>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.source" />,
    dataIndex: 'taskType',
    render: (type) => <TypeTag type={type} />,
    sorter: (a, b) => a.taskType - b.taskType,
    ellipsis: true,
  }
}

export default Source
