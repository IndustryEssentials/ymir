import { ImportingItem } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { Button, Table, TableColumnsType } from 'antd'
import { FC } from 'react'
import { useSelector } from 'umi'
import t from '@/utils/t'
import EditCell from '@/components/form/EditCell'
import StrategyRadio from './StrategyRadio'
import { getTypeLabel, Types } from './AddTypes'
import PublicDatasetClassSelector from './PublicDatasetClassSelector'

const AddList: FC = () => {
  const { items: list } = useSelector(({ dataset }) => dataset.importing)
  const { run: remove } = useRequest<null, [(number | undefined)[]]>('dataset/removeImporting', { loading: false })
  const { run: updateImportingItem } = useRequest<null, [ImportingItem]>('dataset/updateImportingItem', { loading: false })
  const columns: TableColumnsType<ImportingItem> = [
    {
      title: t('dataset.add.form.type.label'),
      dataIndex: 'type',
      width: 200,
      render: (type) => t(getTypeLabel(type)),
    },
    {
      title: t('dataset.add.form.name.label'),
      dataIndex: 'name',
      width: 300,
      render(name, item) {
        return (
          <EditCell
            value={name}
            onChange={(updatedName) => {
              updateImportingItem({
                ...item,
                name: updatedName,
              })
            }}
            validate={(value) => {
              return true
            }}
          />
        )
      },
    },
    {
      title: 'Source(url/path/file name/dataset name)',
      dataIndex: 'sourceName',
    },
    {
      title: t('dataset.add.form.label.label'),
      dataIndex: 'strategy',
      render: (strategy, item) => {
        return item.type === Types.INTERNAL ? (
          <PublicDatasetClassSelector
            id={Number(item.source)}
            onChange={(classes) => {
              updateImportingItem({
                ...item,
                classes,
              })
            }}
          />
        ) : (
          <StrategyRadio
            type={item.type}
            onChange={({ target }) => {
              updateImportingItem({
                ...item,
                strategy: target.value,
              })
            }}
          />
        )
      },
    },
    {
      title: t('common.action'),
      dataIndex: 'action',
      render: (_, { index }) => {
        return (
          <Button type="link" onClick={() => remove([index])}>
            {t('common.del')}
          </Button>
        )
      },
    },
  ]

  return <Table rowKey={(item) => item.index || 0} dataSource={list} columns={columns} pagination={false} />
}
export default AddList
