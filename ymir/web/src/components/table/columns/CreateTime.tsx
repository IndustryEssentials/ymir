import { ColumnType } from 'antd/lib/table'

import { diffTime } from '@/utils/date'
import StrongTitle from './StrongTitle'

function CreateTime<T extends YModels.Result>(sort: boolean = true): ColumnType<T> {
  const sortConfig = {
    sorter: (a: T, b: T) => diffTime(a.createTime, b.createTime),
    sortDirections: ['ascend', 'descend', 'ascend'],
    defaultSortOrder: 'descend',
  }
  const defaultConfig = {
    title: <StrongTitle label="dataset.column.create_time" />,
    dataIndex: 'createTime',
    width: 180,
  }
  return sort ? { ...defaultConfig, ...sortConfig } : defaultConfig
}

export default CreateTime
