import React, { useEffect, useState } from "react"
import { Card, Table, TableColumnsType } from "antd"
import { useParams, useSelector } from "umi"

import { Dataset, InferDataset as DatasetType } from "@/interface/dataset"
import { ModelVersion } from "@/interface/model"

import useFetch from "@/hooks/useFetch"
import t from '@/utils/t'
import { getInferDatasetColumns } from "@/components/table/Columns"

import s from './index.less'

type ResultCache<T> = { [key: string | number]: T }
type DatasetState = {
  dataset: {
    dataset: ResultCache<Dataset>
  }
}
type ModelState = {
  model: {
    model: ResultCache<ModelVersion>,
  }
}
const initQuery = { current: 1, offset: 0, limit: 2 }

const InferDataset: React.FC = () => {
  const { id: pid } = useParams<{ id?: string }>()
  const [datasets, setDatasets] = useState<DatasetType[]>([])
  const [query, setQuery] = useState(initQuery)
  const [{ items, total }, getDatasets] = useFetch('dataset/queryInferDatasets', { items: [], total: 0 })
  const cols = getInferDatasetColumns()
  const cacheDatasets = useSelector((state: DatasetState) => state.dataset.dataset)
  const cacheModels = useSelector((state: ModelState) => state.model.model)
  const actionCol: TableColumnsType<DatasetType> = [{
    dataIndex: 'action',
    title: 'action',
    render: () => <div>action</div>,
  }]
  const columns = [...cols, ...actionCol]

  useEffect(() => pid && fetchInferDatasets(), [pid, query])

  useEffect(() => setDatasets(items), [items])

  useEffect(() => {
    setDatasets((datasets) => datasets.map(dataset => {
      const { inferDatasetId, inferModelId } = dataset
      const inferModel = inferModelId[0] ? cacheModels[inferModelId[0]] : undefined
      const inferDataset = inferDatasetId ? cacheDatasets[inferDatasetId] : undefined
      return { ...dataset, inferModel, inferDataset }
    }))
  }, [cacheDatasets, cacheModels, items])

  function pageChange(current: number, size: number) {
    const limit = size
    const offset = (current - 1) * size
    setQuery(query => ({ ...query, current, limit, offset }))
  }

  function fetchInferDatasets() {
    return getDatasets({ pid, ...query })
  }

  return <div className={s.inferDataset}>
    <Card title={t('model.diagnose.tab.infer_datasets')}>
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
    </Card>
  </div>
}

export default InferDataset
