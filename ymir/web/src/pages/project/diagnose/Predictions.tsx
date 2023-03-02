import React, { useEffect, useRef, useState } from 'react'
import { Card, Table, TableColumnsType } from 'antd'
import { useHistory, useParams } from 'umi'
import { useSelector } from 'react-redux'

import useFetch from '@/hooks/useFetch'
import t from '@/utils/t'
import { INFER_CLASSES_MAX_COUNT, INFER_DATASET_MAX_COUNT, updateResultByTask } from '@/constants/common'

import { getInferDatasetColumns } from '@/components/table/Columns'
import Actions from '@/components/table/Actions'
import Hide, { RefProps } from '@/components/common/hide'

import s from './index.less'
import { EyeOnIcon, DiagnosisIcon, DeleteIcon } from '@/components/common/Icons'
import { validDataset } from '@/constants/dataset'

const initQuery = { current: 1, offset: 0, limit: 20 }

const InferDataset: React.FC = () => {
  const { id: pid } = useParams<{ id?: string }>()
  const history = useHistory()
  const [datasets, setDatasets] = useState<YModels.InferDataset[]>([])
  const [query, setQuery] = useState(initQuery)
  const hideRef = useRef<RefProps>(null)
  const [{ items, total }, getDatasets] = useFetch('dataset/queryInferDatasets', { items: [], total: 0 })
  const cols = getInferDatasetColumns(datasets[0]?.type)
  const cacheDatasets = useSelector<YStates.Root, YStates.IdMap<YModels.Dataset>>((state) => state.dataset.dataset)
  const cacheModels = useSelector<YStates.Root, YStates.IdMap<YModels.Model>>((state) => state.model.model)
  const progressTasks = useSelector<YStates.Root, YModels.ProgressTask[]>(({ socket }) => socket.tasks)
  const actions = (record: YModels.InferDataset): YComponents.Action[] => [
    {
      key: 'diagnose',
      label: t('common.action.diagnose'),
      onclick: () =>
        history.push(`/home/project/${pid}/diagnose#metrics`, {
          mid: record.inferModelId,
        }),
      disabled: !validDataset(record) || (record.assetCount > INFER_DATASET_MAX_COUNT || (record.inferModel?.keywords?.length || 0) > INFER_CLASSES_MAX_COUNT),
      icon: <DiagnosisIcon />,
    },
    {
      key: 'preview',
      label: t('common.action.preview'),
      hidden: () => !validDataset(record),
      onclick: () => history.push(`/home/project/${pid}/dataset/${record.id}/assets#pred`),
      icon: <EyeOnIcon />,
    },
    {
      key: 'del',
      label: t('common.action.del'),
      onclick: () => hide(record),
      icon: <DeleteIcon />,
    },
  ]
  const actionCol: TableColumnsType<YModels.InferDataset> = [
    {
      dataIndex: 'action',
      title: t('common.action'),
      render: (_, record) => <Actions actions={actions(record)} showCount={4} />,
    },
  ]
  const columns = [...cols, ...actionCol]

  useEffect(() => pid && fetchInferDatasets(), [pid, query])

  useEffect(() => {
    if (datasets.length && progressTasks.length) {
      const needReload = progressTasks.some(({ reload }) => reload)
      if (needReload) {
        fetchInferDatasets()
      } else {
        const updatedDatasets = datasets.map((dataset) => {
          const ds = updateResultByTask<typeof dataset>(
            dataset,
            progressTasks.find((task) => task.hash === dataset.task.hash),
          )
          return ds ? ds : dataset
        })
        setDatasets(updatedDatasets)
      }
    }
  }, [progressTasks])

  useEffect(() => setDatasets(items), [items])

  useEffect(() => {
    setDatasets((datasets) =>
      datasets.map((dataset) => {
        const { inferDatasetId, inferModelId } = dataset
        const inferModel = inferModelId[0] ? cacheModels[inferModelId[0]] : undefined
        const inferDataset = inferDatasetId ? cacheDatasets[inferDatasetId] : undefined
        return { ...dataset, inferModel, inferDataset }
      }),
    )
  }, [cacheDatasets, cacheModels, items])

  function pageChange(current: number, size: number) {
    const limit = size
    const offset = (current - 1) * size
    setQuery((query) => ({ ...query, current, limit, offset }))
  }

  function fetchInferDatasets() {
    return getDatasets({ pid, ...query })
  }

  const hide = (dataset: YModels.InferDataset) => {
    hideRef?.current?.hide([dataset])
  }

  return (
    <div className={s.inferDataset}>
      <Table
        columns={columns}
        dataSource={datasets}
        rowKey={(record) => record.id}
        pagination={{
          onChange: pageChange,
          current: query.current,
          defaultPageSize: query.limit,
          total,
          showQuickJumper: true,
          showSizeChanger: true,
        }}
      />
      <Hide ref={hideRef} ok={fetchInferDatasets} msg="pred.action.del.confirm.content" />
    </div>
  )
}

export default InferDataset
