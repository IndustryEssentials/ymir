import { ColumnType } from 'antd/lib/table'

import { humanize } from '@/utils/number'
import StrongTitle from './StrongTitle'
import { Dataset } from '@/constants'

function Count<T extends Dataset>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.asset_count" />,
    dataIndex: 'assetCount',
    render: (num) => humanize(num),
    sorter: (a, b) => a.assetCount - b.assetCount,
    width: 120,
  }
}

export default Count
