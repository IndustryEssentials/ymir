import getColumns from "@/components/table/Columns"
import useFetch from "@/hooks/useFetch"
import { Dataset, InferDataset as DatasetType, InferDataset } from "@/interface/dataset"
import { ModelVersion } from "@/interface/model"
import { Card, Table, TableColumnsType } from "antd"
import React, { useEffect, useState } from "react"
import { useParams, useSelector } from "umi"

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

const InferDataset: React.FC = () => {
  const { id: pid } = useParams<{ id?: string }>()
  const [datasets, setDatasets] = useState<InferDataset[]>([])
  const [{ items, total }, getDatasets] = useFetch('dataset/queryInferDatasets', { items: [], total: 0 })
  const cols = getColumns<DatasetType>('inferDataset')
  const cacheDatasets = useSelector((state: DatasetState) => state.dataset.dataset)
  const cacheModels = useSelector((state: ModelState) => state.model.model)
  const actionCol: TableColumnsType<DatasetType> = [{
    dataIndex: 'action',
    title: 'action',
    render: () => <div>action</div>,
  }]
  const columns = { ...cols, actionCol }
  useEffect(() => pid && getDatasets({ projectId: pid, }), [pid])

  useEffect(() => setDatasets(items), [items])

  useEffect(() => {
    setDatasets((datasets) => datasets.map(dataset => {
      const model = dataset.modelId ? cacheModels[dataset.modelId] : undefined
      const validDataset = dataset.validationDatasetId ? cacheDatasets[dataset.validationDataset] : undefined
      return { ...dataset, model, validDataset }
    }))
    console.log('cacheDatasets, cacheModels:', cacheDatasets, cacheModels)
  }, [cacheDatasets, cacheModels])

  return <div className={s.inferDataset}>
    <Card title="推理结果">
      <Table
        columns={columns}
        dataSource={datasets}
      />
    </Card>
  </div>
}

export default InferDataset
