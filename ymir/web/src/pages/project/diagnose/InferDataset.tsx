import React, { useEffect, useState } from 'react'
import { Card, Table, TableColumnsType } from 'antd'
import { useHistory, useParams, useSelector } from 'umi'

import useFetch from '@/hooks/useFetch'
import t from '@/utils/t'
import { getInferDatasetColumns } from '@/components/table/Columns'
import Actions from '@/components/table/Actions'

// test lint-staged
import s from './index.less'
import { EyeOnIcon, DiagnosisIcon } from '@/components/common/Icons'
import { INFER_CLASSES_MAX_COUNT, INFER_DATASET_MAX_COUNT } from '@/constants/common'
import { isDetection } from '@/constants/objectType'

const initQuery = { current: 1, offset: 0, limit: 20 }

const InferDataset: React.FC = () => {
  const { id: pid } = useParams<{ id?: string }>()
  const history = useHistory()
  const [datasets, setDatasets] = useState<YModels.InferDataset[]>([])
  const [query, setQuery] = useState(initQuery)
  const [{ items, total }, getDatasets] = useFetch('dataset/queryInferDatasets', { items: [], total: 0 })
  const cols = getInferDatasetColumns(datasets[0]?.type)
  const cacheDatasets = useSelector((state: YStates.DatasetState) => state.dataset.dataset)
  const cacheModels = useSelector((state: YStates.ModelState) => state.model.model)
  const actions = (record: YModels.InferDataset): YComponents.Action[] => [
    {
      key: 'diagnose',
      label: t('common.action.diagnose'),
      onclick: () =>
        history.push(`/home/project/${pid}/diagnose#metrics`, {
          mid: record.inferModelId,
        }),
      hidden: () => !isDetection(record.type),
      disabled: record.assetCount > INFER_DATASET_MAX_COUNT || (record.inferModel?.keywords?.length || 0) > INFER_CLASSES_MAX_COUNT,
      icon: <DiagnosisIcon />,
    },
    {
      key: 'detail',
      label: t('dataset.action.detail'),
      onclick: () => history.push(`/home/project/${pid}/dataset/${record.id}`),
    },
    {
      key: 'preview',
      label: t('common.action.preview'),
      onclick: () => history.push(`/home/project/${pid}/dataset/${record.id}/assets`),
      icon: <EyeOnIcon />,
    },
  ]
  const actionCol: TableColumnsType<YModels.InferDataset> = [
    {
      dataIndex: 'action',
      title: t('common.action'),
      render: (_, record) => <Actions actions={actions(record)} />,
    },
  ]
  const columns = [...cols, ...actionCol]

  useEffect(() => pid && fetchInferDatasets(), [pid, query])

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
    </div>
  )
}

export default InferDataset
