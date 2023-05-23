import { ImportingItem } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { Button, Table, TableColumnsType } from 'antd'
import { FC, useCallback } from 'react'
import { useParams, useSelector } from 'umi'
import t from '@/utils/t'

const AddList: FC = () => {
  const params = useParams<{ id: string }>()
  const pid = Number(params.id)
  const { items: list } = useSelector(({ dataset }) => dataset.importing)
  const { run: batchImport } = useRequest('task/batchAdd')
  const { run: remove } = useRequest<null, [(number | undefined)[]]>('dataset/removeImporting')
  const columns: TableColumnsType<ImportingItem> = [
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
    {
      title: t('common.action'),
      dataIndex: 'action',
      render: (_, { index }) => {
        return (
          <Button type="link" onClick={() => remove([index])}>
            Delete
          </Button>
        )
      },
    },
  ]

  const batch = useCallback(() => {
    batchImport({ pid, items: list })
  }, [list])
  return (
    <>
      <Table rowKey={(item) => item.index || 0} dataSource={list} columns={columns} pagination={false} />
      <Button type="primary" onClick={batch}>
        Batch Import
      </Button>
    </>
  )
}
export default AddList
