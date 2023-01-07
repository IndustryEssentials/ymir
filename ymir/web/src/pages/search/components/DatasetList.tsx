import { useEffect, useRef, useState } from 'react'
import { useHistory } from 'umi'
import { FC } from 'react'
import { Table, TableProps, TableColumnsType, Popover, Tooltip } from 'antd'
import { Link } from 'umi'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { diffTime } from '@/utils/date'
import { TASKSTATES } from '@/constants/task'
import { ResultStates } from '@/constants/common'
import { validDataset } from '@/constants/dataset'

import RenderProgress from '@/components/common/Progress'
import TypeTag from '@/components/task/TypeTag'
import Actions from '@/components/table/Actions'
import AssetCount from '@/components/dataset/AssetCount'
import EditDescBox from '@/components/form/editDescBox'
import Terminate, { RefProps } from '@/components/task/terminate'

import { ScreenIcon, TaggingIcon, TrainIcon, VectorIcon, WajueIcon, SearchIcon, EditIcon, CopyIcon, StopIcon, CompareListIcon } from '@/components/common/Icons'
import { DescPop } from '@/components/common/DescPop'

type Props = {
  pid: number
  name?: string
  query?: YParams.ResultListQuery
}
type DatasetsType = {
  items: YModels.Dataset[]
  total: number
}

function showTitle(str: string) {
  return <strong>{t(str)}</strong>
}
const DatasetList: FC<Props> = ({ pid, name, query }) => {
  const history = useHistory()
  const [datasetQuery, setQuery] = useState<YParams.DatasetsQuery>({
    pid,
    ...(query || {}),
  })
  const { data: datasets, run: getDatasets } = useRequest<DatasetsType, [YParams.DatasetsQuery]>('dataset/queryDatasets', {
    debounceWait: 100
  })
  const [testingSetIds, setTestingSetIds] = useState<number[]>([])
  const [editingDataset, setEditingDataset] = useState<YModels.Dataset>()
  const terminateRef = useRef<RefProps>(null)

  useEffect(
    () =>
      query ?
      setQuery((q) => ({
        ...q,
        ...query,
      })) : setQuery({ pid }),
    [query],
  )
  useEffect(() => datasetQuery && fetch(), [datasetQuery])

  const tableChange: TableProps<YModels.Dataset>['onChange'] = ({ current, pageSize }, filters, sorters = {}) => {}
  const pageChange = (page: number, pageSize: number) => {
    const offset = (page - 1) * (datasetQuery.limit || 10)
    setQuery((query) => ({
      ...query,
      offset,
      limit: pageSize,
    }))
  }

  const columns: TableColumnsType<YModels.Dataset> = [
    {
      title: showTitle('project.tab.set.title'),
      key: 'name',
      dataIndex: 'versionName',
      render: (vname, { id, name, description }) => {
        const popContent = <DescPop description={description} style={{ maxWidth: '30vw' }} />
        const content = (
          <Link to={`/home/project/${pid}/dataset/${id}`}>
            {name} {vname}
          </Link>
        )
        return description ? (
          <Popover title={t('common.desc')} content={popContent}>
            {content}
          </Popover>
        ) : (
          content
        )
      },
      ellipsis: true,
    },
    {
      title: showTitle('dataset.column.source'),
      dataIndex: 'taskType',
      render: (type) => <TypeTag type={type} />,
      ellipsis: true,
    },
    {
      title: showTitle('dataset.column.asset_count'),
      dataIndex: 'assetCount',
      render: (num, record) => <AssetCount dataset={record} />,
      width: 120,
    },
    {
      title: showTitle('dataset.column.keyword'),
      dataIndex: 'keywords',
      render: (_, dataset) => {
        const { gt, pred } = dataset
        const renderLine = (keywords: string[] = [], label = 'gt') => (
          <div>
            <div>{t(`annotation.${label}`)}:</div>
            {t('dataset.column.keyword.label', {
              keywords: keywords.join(', '),
              total: keywords.length,
            })}
          </div>
        )
        const label = (
          <>
            {renderLine(gt?.keywords)}
            {renderLine(pred?.keywords, 'pred')}
          </>
        )
        return validDataset(dataset) ? (
          <Tooltip title={label} color="white" overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }} mouseEnterDelay={0.5}>
            <div>{label}</div>
          </Tooltip>
        ) : null
      },
      ellipsis: {
        showTitle: false,
      },
    },
    {
      title: showTitle('dataset.column.state'),
      dataIndex: 'state',
      render: (state, record) => RenderProgress(state, record),
      // width: 60,
    },
    {
      title: showTitle('dataset.column.create_time'),
      dataIndex: 'createTime',
      sorter: (a, b) => diffTime(a.createTime, b.createTime),
      sortDirections: ['ascend', 'descend', 'ascend'],
      defaultSortOrder: 'descend',
      width: 180,
    },
    {
      title: showTitle('dataset.column.action'),
      key: 'action',
      dataIndex: 'action',
      render: (text, record) => <Actions actions={actionMenus(record)} />,
      align: 'center',
      width: 300,
    },
  ]

  const actionMenus = (record: YModels.Dataset) => {
    const { id, groupId, state, taskState, task, assetCount } = record
    const invalidDataset = (ds: YModels.Dataset) => !validDataset(ds) || ds.assetCount === 0
    const menus = [
      {
        key: 'label',
        label: t('dataset.action.label'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/label?did=${id}`),
        icon: <TaggingIcon />,
      },
      {
        key: 'train',
        label: t('dataset.action.train'),
        hidden: () => invalidDataset(record) || isTestingDataset(id),
        onclick: () => history.push(`/home/project/${pid}/train?did=${id}`),
        icon: <TrainIcon />,
      },
      {
        key: 'mining',
        label: t('dataset.action.mining'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/mining?did=${id}`),
        icon: <VectorIcon />,
      },
      {
        key: 'preview',
        label: t('common.action.preview'),
        hidden: () => !validDataset(record),
        onclick: () => history.push(`/home/project/${pid}/dataset/${id}/assets`),
        icon: <SearchIcon />,
      },
      {
        key: 'merge',
        label: t('common.action.merge'),
        hidden: () => !validDataset(record),
        onclick: () => history.push(`/home/project/${pid}/merge?did=${id}`),
        icon: <CompareListIcon />,
      },
      {
        key: 'filter',
        label: t('common.action.filter'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/filter?did=${id}`),
        icon: <ScreenIcon />,
      },
      {
        key: 'inference',
        label: t('dataset.action.inference'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/inference?did=${id}`),
        icon: <WajueIcon />,
      },
      {
        key: 'copy',
        label: t('task.action.copy'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/copy?did=${id}`),
        icon: <CopyIcon />,
      },
      {
        key: 'edit',
        label: t('common.action.edit.desc'),
        onclick: () => editDesc(record),
        icon: <EditIcon />,
      },
      {
        key: 'stop',
        label: t('task.action.terminate'),
        onclick: () => stop(record),
        hidden: () => taskState === TASKSTATES.PENDING || state !== ResultStates.READY || task.is_terminated,
        icon: <StopIcon />,
      },
    ]
    return menus
  }

  function isTestingDataset(id: number) {
    return testingSetIds?.includes(id)
  }

  function fetch() {
    getDatasets(datasetQuery)
  }

  const stop = (dataset: YModels.Dataset) => {
    terminateRef?.current?.confirm(dataset)
  }

  const editDesc = (dataset: YModels.Dataset) => {
    setEditingDataset(undefined)
    setTimeout(() => setEditingDataset(dataset), 0)
  }

  return (
    <div>
      <Table
        dataSource={datasets?.items}
        onChange={tableChange}
        rowKey={(record) => record.id}
        rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
        columns={columns}
        pagination={{
          showQuickJumper: true,
          showSizeChanger: true,
          total: datasets?.total,
          pageSize: query?.limit,
          onChange: pageChange,
        }}
      />
      {editingDataset ? <EditDescBox record={editingDataset} handle={fetch} /> : null}
      <Terminate ref={terminateRef} ok={fetch} />
    </div>
  )
}

export default DatasetList
