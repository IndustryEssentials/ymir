import type { DefaultOptionType } from 'antd/lib/select'
import type { FC, ReactNode, UIEventHandler, WheelEvent, WheelEventHandler } from 'react'

import { useEffect, useState } from 'react'
import { Col, ConfigProvider, Row, Select, SelectProps } from 'antd'
import { useSelector } from 'react-redux'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import EmptyState from '@/components/empty/dataset'
import Dataset from '@/components/form/option/Dataset'
import ModelVersionName from '../result/ModelVersionName'
import VersionName from '../result/VersionName'

interface Props extends Omit<SelectProps, 'mode'> {
  pid: number
  autoSelectFirst?: boolean
}
// interface DatasetOption extends YModels.Dataset {
//   disabled?: boolean
// }
type ModelId = string
type DataType = YModels.Prediction
type PredictionItems = {
  [id: ModelId]: DataType[]
}
type PredictionList = {
  items: DataType[]
  total: number
}

const PredictionSelect: FC<Props> = ({ pid, autoSelectFirst = true, ...resProps }) => {
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [options, setOptions] = useState<DefaultOptionType[]>([])
  const [defaultSelected, setDefaultSelcted] = useState<number>()
  const [predictions, setPredictions] = useState<PredictionItems>({})
  const {
    data: remotePredictions,
    run: getPredictions,
    loading,
  } = useRequest<PredictionList, [YParams.PredictionsQuery]>('prediction/getPredictions', {
    debounceWait: 300,
    loading: false,
    cacheKey: 'predictionSelect',
    refreshDeps: [pid],
    ready: !!pid,
  })

  useEffect(() => {
    pid && queryPredictions(currentPage)
  }, [pid, currentPage])

  useEffect(() => {
    if (!remotePredictions) {
      return
    }
    const { items: remoteItems, total } = remotePredictions
    const groupItems = remoteItems.reduce<PredictionItems>((prev, item) => {
      const mid = item.inferModelId[0]
      const items = item.rowSpan ? [item] : [...prev[mid], item]
      return {
        ...prev,
        [mid]: items,
      }
    }, {})
    setTotal(total)
    setPredictions((old) => ({ ...old, ...groupItems }))
  }, [remotePredictions])

  useEffect(() => {
    if (autoSelectFirst && options.length) {
      setDefaultSelcted(options[0].options[0])
    }
  }, [options, autoSelectFirst])

  useEffect(() => {
    const modelsId = Object.keys(predictions)
    const options = modelsId.map((mid) => {
      const preds = predictions[mid]
      return {
        label: <ModelVersionName id={Number(mid)} />,
        options: preds.map((pred) => ({
          label: <VersionName id={pred.inferDatasetId} />,
          value: pred.id,
        })),
      }
    })

    setOptions(options)
  }, [predictions])

  function queryPredictions(page = 1) {
    const limit = 10
    const offset = (page - 1) * limit
    if (total && offset > total) {
      return
    }
    getPredictions({ pid, limit, offset })
  }

  const scroll: UIEventHandler<HTMLDivElement> = (e) => {
    const { currentTarget } = e
    if (scrollEnd(currentTarget)) {
      setCurrentPage((page) => page + 1)
    }
  }

  const scrollEnd = (target: HTMLDivElement) => target.scrollTop + target.offsetHeight === target.scrollHeight

  return (
    <ConfigProvider renderEmpty={() => <EmptyState />}>
      <Select
        {...resProps}
        key={defaultSelected}
        defaultValue={defaultSelected}
        showArrow
        allowClear
        options={options}
        onPopupScroll={scroll}
        loading={loading}
        placeholder={t('pred.selector.placeholder')}
      ></Select>
    </ConfigProvider>
  )
}

export default PredictionSelect
