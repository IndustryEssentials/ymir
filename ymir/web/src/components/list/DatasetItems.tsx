import { FC, useEffect, useState } from 'react'
import { useSelector } from 'umi'
import { Table } from 'antd'
import { getDatasetColumns } from '../table/Columns'

type Props = {
  gid: number
  selectChange?: (keys: number[]) => void
}

const DatasetItems: FC<Props> = ({ gid, selectChange }) => {
  const versions = useSelector(({ dataset }) => dataset.versions[gid])
  const columns = getDatasetColumns()
  const [selected, setSelected] = useState<number[]>([])

  useEffect(() => selectChange && selectChange(selected), [selected])

  return (
    <Table
      dataSource={versions}
      // onChange={tableChange}
      rowKey={(record) => record.id}
      rowSelection={{
        selectedRowKeys: selected,
        onChange: (keys) => setSelected(keys as number[]),
      }}
      rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
      columns={columns}
      pagination={false}
    />
  )
}

export default DatasetItems
