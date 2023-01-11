import { ColumnType } from 'antd/lib/table'

import { humanize } from '@/utils/number'
import StrongTitle from './StrongTitle'

function Count<T extends YModels.Dataset>(): ColumnType<T> {
  return {
    title: <StrongTitle label="dataset.column.asset_count" />,
    dataIndex: 'assetCount',
    render: (num) => humanize(num),
    sorter: (a, b) => a.assetCount - b.assetCount,
    width: 120,
  }
}

export default Count
