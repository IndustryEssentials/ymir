import React, { FC, useEffect, useState } from 'react'
import { Table, Space, Button, message, Card, TableColumnsType, TableProps, TableColumnType } from 'antd'
import { useHistory } from 'umi'
import { useSelector } from 'react-redux'

import t from '@/utils/t'
import Actions from '@/components/table/Actions'
import AssetCount from '@/components/dataset/AssetCount'
import s from '../index.less'
import { EyeOnIcon } from '@/components/common/Icons'
import VersionName from '@/components/result/VersionName'
import useRequest from '@/hooks/useRequest'
import StrongTitle from '@/components/table/columns/StrongTitle'
import { ObjectType } from '@/constants/objectType'
import Stages from '@/components/table/columns/Stages'
import InferDataset from '@/components/table/columns/InferDataset'
import Model from '@/components/table/columns/InferModel'

export type AType = 'dataset' | 'model' | 'prediction'
type DataType = YModels.Dataset | YModels.Model | YModels.Prediction
type ColumnType = TableColumnType<DataType>
type ColumnsType = TableColumnsType<DataType>
type Props = {
  active?: AType
  pid: number | string
}
const tabs = [
  { tab: 'project.tab.set.title', key: 'dataset' },
  { tab: 'project.tab.model.title', key: 'model' },
  { tab: 'annotation.pred', key: 'prediction' },
]

const HiddenList: FC<Props> = ({ active, pid }) => {
  const history = useHistory()
  const [list, setHiddenList] = useState<DataType[]>([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState<YParams.DatasetsQuery>({
    offset: 0,
    limit: 10,
  })
  const [selected, setSelected] = useState<(number | string)[]>([])
  const [columns, setColumns] = useState<ColumnsType>([])
  const cacheDatasets = useSelector<YStates.Root, YStates.IdMap<YModels.Dataset>>((state) => state.dataset.dataset)
  const cacheModels = useSelector<YStates.Root, YStates.IdMap<YModels.Model>>((state) => state.model.model)
  const { data: project, run: getProject } = useRequest<YModels.Project, [{ id: number | string }]>('project/getProject')
  const { data: recoverResult, run: recoverAPI } = useRequest(`${active}/restore`)
  const { data: listData, run: getList } = useRequest<YStates.List<DataType>, [{ [key: string]: any }]>(`${active}/getHiddenList`)

  useEffect(() => {
    pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    if (active === 'prediction' && list.length) {
      const predictions = list as YModels.Prediction[]
      const updatedPredictions = predictions.map((prediction: YModels.Prediction) => {
        const { inferDatasetId, inferModelId } = prediction
        const inferModel = inferModelId[0] ? cacheModels[inferModelId[0]] : undefined
        const inferDataset = inferDatasetId ? cacheDatasets[inferDatasetId] : undefined
        return { ...prediction, inferModel, inferDataset }
      })
      setHiddenList(updatedPredictions)
    }
  }, [cacheDatasets, cacheModels, list.length, active])

  useEffect(() => {
    if (listData) {
      setHiddenList(listData.items)
      setTotal(listData.total)
      if (query?.offset && listData.total <= query.offset) {
        const offset = query.offset - (query.limit || 10)
        return setQuery((old) => ({ ...old, offset }))
      }
    }
  }, [listData])

  useEffect(() => {
    if (project && active) {
      const columns = getColumns(active, project.type)
      setColumns(columns)
    }
  }, [active, project])

  useEffect(() => {
    if (recoverResult) {
      fetch()
      setSelected([])
    }
  }, [recoverResult])

  useEffect(() => {
    active && query && fetch()
  }, [active, query])

  const tabChange = (key: string) => {
    // initial query
    setQuery({})
    setSelected([])
    setHiddenList([])
    history.push(`#${key}`)
  }

  const titleCol = {
    title: <StrongTitle label="dataset.column.name" />,
    dataIndex: 'name',
    render: (name: string, dataset: YModels.Dataset) => <VersionName result={dataset} />,
    ellipsis: { showTitle: true },
  }
  const countCol = {
    title: <StrongTitle label="dataset.column.asset_count" />,
    dataIndex: 'assetCount',
    render: (num: number, dataset: YModels.Dataset) => <AssetCount dataset={dataset} />,
  }

  const timeCol = {
    title: <StrongTitle label="dataset.column.delete_time" />,
    dataIndex: 'updateTime',
    // sorter: true,
    // sortDirections: ['descend', 'ascend'],
    // defaultSortOrder: 'descend',
  }
  const actionCol: ColumnType = {
    title: <StrongTitle label="dataset.column.action" />,
    dataIndex: 'id',
    render: (id: number, record: DataType) => <Actions actions={actionMenus(record)} />,
    align: 'center',
  }

  const getColumns = (type: AType, objectType: YModels.ObjectType = ObjectType.ObjectDetection): ColumnsType => {
    let columns: ColumnType[] = []
    if (type === 'dataset') {
      columns = [titleCol, countCol] as ColumnsType
    } else if (type === 'model') {
      columns = [titleCol, Stages()] as ColumnsType
    } else if (type === 'prediction') {
      columns = [Model(), InferDataset()] as ColumnsType
    }
    return [...columns, timeCol, actionCol]
  }

  const actionMenus = ({ id }: DataType) => [
    {
      key: 'restore',
      label: t('common.action.restore'),
      onclick: () => recover([id]),
      icon: <EyeOnIcon />,
    },
  ]

  function fetch() {
    getList({ ...query, pid })
  }

  function recover(ids: (number | string)[] = []) {
    recoverAPI({ pid, ids })
  }

  function multipleRestore() {
    recover(selected)
  }

  const pageChange: TableProps<DataType>['onChange'] = ({ current = 1, pageSize = 10 }, filters, sorters) => {
    if (Array.isArray(sorters)) {
      return
    }
    const is_desc = sorters.order !== 'ascend'
    const sortColumn = sorters.field === 'updateTime' ? 'update_datetime' : undefined
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery((old) => ({
      ...old,
      limit,
      offset,
      order_by: sorters.column ? sortColumn : 'id',
      is_desc,
    }))
  }

  return (
    <div className={s.hiddenList}>
      <Space className="actions">
        <Button disabled={!selected.length} type="primary" onClick={multipleRestore}>
          <EyeOnIcon /> {t('common.action.multiple.restore')}
        </Button>
      </Space>
      <div className={`list ${s.table}`}>
        <Card
          tabList={tabs.map((tab) => ({ ...tab, tab: t(tab.tab) }))}
          activeTabKey={active}
          onTabChange={tabChange}
          className="noShadow"
          bordered={false}
          style={{ margin: '-20px -20px 0', background: 'transparent' }}
          headStyle={{ padding: '0 20px', background: '#fff', marginBottom: '20px' }}
          bodyStyle={{ padding: '0 20px' }}
        >
          <Table
            dataSource={list}
            pagination={{
              total,
              showQuickJumper: true,
              showSizeChanger: true,
              defaultCurrent: 1,
              defaultPageSize: query?.offset || 10,
            }}
            onChange={pageChange}
            rowKey={(record) => record.id}
            rowSelection={{
              selectedRowKeys: selected,
              onChange: setSelected,
            }}
            rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
            columns={columns}
          ></Table>
        </Card>
      </div>
    </div>
  )
}

export default HiddenList
