import React, { useEffect, useRef, useState } from 'react'
import { Card, ConfigProvider, Pagination, Table, TableColumnsType } from 'antd'
import { useHistory, useParams, useSelector } from 'umi'
import {} from 'react-redux'

import t from '@/utils/t'
import { INFER_CLASSES_MAX_COUNT, INFER_DATASET_MAX_COUNT, updateResultByTask, validState } from '@/constants/common'
import useRequest from '@/hooks/useRequest'

import { getPredictionColumns } from '@/components/table/Columns'
import Actions from '@/components/table/Actions'
import Hide, { RefProps } from '@/components/common/hide'
import MetricsModal from './components/MetricsModal'
import Empty from '@/components/empty/Pred'

import s from './index.less'
import { EyeOnIcon, DiagnosisIcon, DeleteIcon } from '@/components/common/Icons'
import { List } from '@/models/typings/common.d'
import { Prediction } from '@/constants'

const initQuery = { current: 1, offset: 0, limit: 20 }

const Predictions: React.FC = () => {
  const { id: pid } = useParams<{ id?: string }>()
  const history = useHistory()
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [query, setQuery] = useState(initQuery)
  const hideRef = useRef<RefProps>(null)
  const { data: { items, total } = { items: [], total: 0 }, run: getPredictions } = useRequest<List<Prediction>>('prediction/getPredictions')
  const cols = getPredictionColumns(predictions[0]?.type)
  const [currentPrediction, setCurrentPrediction] = useState<Prediction>()
  const [metricsModalVisible, setMModalVisible] = useState(false)
  const cacheDatasets = useSelector((state) => state.dataset.dataset)
  const cacheModels = useSelector((state) => state.model.model)
  const progressTasks = useSelector(({ socket }) => socket.tasks)
  const disableDiagnose = (pred: Prediction) => {
    const exceedAssetCount = pred.assetCount > INFER_DATASET_MAX_COUNT
    const exceedTrainingClasses = (pred.inferModel?.keywords?.length || 0) > INFER_CLASSES_MAX_COUNT
    const invalidGt = !pred.gt?.keywords.length
    return !validState(pred.state) || exceedAssetCount || exceedTrainingClasses || invalidGt
  }
  const actions = (record: Prediction): YComponents.Action[] => [
    {
      key: 'diagnose',
      label: t('common.action.diagnose'),
      onclick: () => popupModal(record),
      disabled: disableDiagnose(record),
      icon: <DiagnosisIcon />,
    },
    {
      key: 'preview',
      label: t('common.action.preview'),
      hidden: () => !validState(record.state),
      onclick: () => history.push(`/home/project/${pid}/prediction/${record.id}#pred`),
      icon: <EyeOnIcon />,
    },
    {
      key: 'del',
      label: t('common.action.del'),
      onclick: () => hide(record),
      icon: <DeleteIcon />,
    },
  ]
  const actionCol: TableColumnsType<Prediction> = [
    {
      dataIndex: 'action',
      title: t('common.action'),
      render: (_, record) => <Actions actions={actions(record)} showCount={4} />,
    },
  ]
  const columns = [...cols, ...actionCol]

  useEffect(() => {
    pid && fetchPredictions()
  }, [pid, query])

  useEffect(() => {
    if (predictions.length && progressTasks.length) {
      const needReload = progressTasks.some(({ reload }) => reload)
      if (needReload) {
        fetchPredictions()
      } else {
        const updatedDatasets = predictions.map((dataset) => {
          const ds = updateResultByTask(
            dataset,
            progressTasks.find((task) => task.hash === dataset.task.hash),
          )
          return ds ? ds : dataset
        })
        setPredictions(updatedDatasets)
      }
    }
  }, [progressTasks])

  useEffect(() => {
    let rowIndex = 0
    setPredictions(
      items.map((prediction) => {
        const { inferDatasetId, inferModelId, rowSpan } = prediction
        if (rowSpan) {
          rowIndex = rowSpan
        }
        const inferModel = inferModelId[0] ? cacheModels[inferModelId[0]] : undefined
        const inferDataset = inferDatasetId ? cacheDatasets[inferDatasetId] : undefined
        return { ...prediction, inferModel, inferDataset }
      }),
    )
  }, [cacheDatasets, cacheModels, items])

  const popupModal = (prediction: Prediction) => {
    setCurrentPrediction(prediction)
    setMModalVisible(true)
  }

  function pageChange(current: number, size: number) {
    const limit = size
    const offset = (current - 1) * size
    setQuery((query) => ({ ...query, current, limit, offset }))
  }

  function fetchPredictions() {
    return getPredictions({ pid, ...query })
  }

  const hide = (dataset: Prediction) => {
    hideRef?.current?.hide([dataset])
  }

  return (
    <div className={s.list}>
      {predictions.length ? (
        <>
          <Table
            columns={columns}
            dataSource={predictions}
            rowKey={(record) => record.id}
            rowClassName={(record) => (record.odd ? 'oddRow' : '')}
            pagination={false}
          />
          <Pagination
            className={`pager`}
            onChange={pageChange}
            current={query.current}
            defaultPageSize={query.limit}
            total={total}
            showQuickJumper
            showSizeChanger
          />
        </>
      ) : (
        <Empty />
      )}
      <Hide ref={hideRef} type="prediction" ok={fetchPredictions} msg="pred.action.del.confirm.content" />
      <MetricsModal width={'90%'} prediction={currentPrediction} visible={metricsModalVisible} onCancel={() => setMModalVisible(false)} footer={null} />
    </div>
  )
}

export default Predictions
