import useRequest from '@/hooks/useRequest'
import { Button, Table, TableColumnsType } from 'antd'
import { FC, useState, useEffect, useCallback } from 'react'
import { useParams } from 'umi'
import { ImportItem as Item } from '.'
type Props = {
  items: Item[]
}

const AddList: FC<Props> = ({ items }) => {
  const params = useParams<{ id: string }>()
  const pid = Number(params.id)
  const [list, setList] = useState<Item[]>([])
  const { run: batchImport } = useRequest('task/batchAdd')
  const columns: TableColumnsType<Item> = [
    {
      title: 'Type',
      dataIndex: 'type',
      width: 200,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      width: 300,
    },
    {
      title: 'Source(url/path/file name/dataset name)',
      dataIndex: 'sourceName',
    },
    {
      title: 'Annotations',
      dataIndex: 'strategy',
      render: () => {
        return <>all/none/ignore</>
      },
    },
  ]

  useEffect(() => {
    setList((list) => [...list, ...items])
  }, [items])

  const batch = useCallback(() => {
    batchImport({ pid, items })
  }, [items])
  return (
    <>
      <Table rowKey={(item) => item.type + item.source} dataSource={list} columns={columns} pagination={false} />
      <Button type="primary" onClick={batch}>
        Batch Import
      </Button>
    </>
  )
}
export default AddList
