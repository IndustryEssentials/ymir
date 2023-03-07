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
}
// interface DatasetOption extends YModels.Dataset {
//   disabled?: boolean
// }
type ModelId = string
type DataType = YModels.Prediction
type PredictionItems = {
  [id: ModelId]: YModels.Prediction[]
}
type PredictionList = {
  items: PredictionItems
  total: number
}

const PredictionSelect: FC<Props> = ({ pid, value, onChange = () => {}, ...resProps }) => {
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [options, setOptions] = useState<DefaultOptionType[]>([])
  const [predictions, setPredictions] = useState<PredictionItems>({})
  const { data: remotePredictions, run: getPredictions, loading } = useRequest<PredictionList>('prediction/getPredictions', {
    debounceWait: 300,
    loading: false,
    cacheKey: 'predictionSelect',
    refreshDeps: [pid],
    ready: !!pid,
    onSuccess: () => {
      setVal(value)
    },
  })
  const [val, setVal] = useState(value)

  useEffect(() => setVal(value), [value])

  useEffect(() => {
    pid && queryPredictions(currentPage)
  }, [pid, currentPage])

  useEffect(() => {
    if (!remotePredictions) {
      return
    }
    const { items: remoteItems, total } = remotePredictions
    setTotal(total)
    setPredictions((items) => ({ ...items, ...remoteItems }))
  }, [remotePredictions])

  useEffect(() => {
    let selected = null
    if (options.length && value) {
      selected = options.find((opt) => value === opt.value)
      if (selected) {
        onChange(value, selected)
      } else {
        onChange(undefined, [])
        setVal(undefined)
      }
    }
  }, [options])

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
    if (offset >= total) {
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
      <Select {...resProps} value={val} onChange={onChange} showArrow allowClear options={options} onPopupScroll={scroll} loading={loading}></Select>
    </ConfigProvider>
  )
}

export default PredictionSelect
