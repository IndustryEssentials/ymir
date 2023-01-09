import { ColumnType } from 'antd/lib/table'

import { diffTime } from '@/utils/date'
import StrongTitle from './StrongTitle'

function CreateTime<T extends YModels.Result>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.create_time" />,
    dataIndex: 'createTime',
    sorter: (a: T, b: T) => diffTime(a.createTime, b.createTime),
    sortDirections: ['ascend', 'descend', 'ascend'],
    defaultSortOrder: 'descend',
    width: 180,
  }
}

export default CreateTime
