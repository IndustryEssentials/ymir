import { FC, ReactNode, useEffect, useState } from 'react'
import { Table, TableColumnsType } from 'antd'
import { isSame } from '@/utils/object'
import Panel from '@/components/form/panel'
import { average, getAverageField, getDetRowforDataset, getModelCell, getSegRowforDataset, opt, percentRender } from './common'
import type { DataType, DataTypeForTable, EvaluationResult, MetricType, ViewProps, MetricKeys, MetricsType, OptionType } from '.'

import t from '@/utils/t'

type KeywordType = {
  value: string | number
  label: string
}
type ListItemType = {
  id: number | string
  config?: { [key: string]: string | number }
  _model: ReactNode
  _average?: number
}

type ListType = {
  id: number | string
  label: string
  rows: ListItemType[]
}

const detFields = ['ap', 'maskap', 'boxap']

const MapView: FC<ViewProps> = ({ type, predictions, datasets, models, data, xByClasses, kw: { ck, keywords }, averageIou }) => {
  const [list, setList] = useState<ListType[]>([])
  const [dd, setDD] = useState<OptionType<number>[]>([])
  const [kd, setKD] = useState<OptionType[]>([])
  const [xasix, setXAsix] = useState<KeywordType[]>([])
  const [dData, setDData] = useState<DataTypeForTable>()
  const [kData, setKData] = useState<DataTypeForTable>()
  const [columns, setColumns] = useState<TableColumnsType<ListItemType>>([])
  const [hiddens, setHiddens] = useState<{ [id: string | number]: boolean }>({})

  useEffect(() => {
    if (data && keywords) {
      generateDData(data)
      generateKData(data)
    } else {
      setDData(undefined)
      setKData(undefined)
    }
  }, [ck, data, keywords, averageIou])

  useEffect(() => {
    setDD(datasets.map(opt))
  }, [datasets])

  useEffect(() => {
    if (data && keywords) {
      const kws = keywords.map((k) => ({ value: k, label: k }))
      setKD(kws)
    }
  }, [keywords, data, ck])

  useEffect(() => {
    const cls = generateColumns()
    setColumns(cls)
  }, [xasix])

  useEffect(() => {
    // list
    if (dData && kData) {
      setList(xByClasses ? generateKwItems() : generateDsItems())
      setXAsix(xByClasses ? dd : kd)
    } else {
      setList([])
    }
  }, [xByClasses, dd, kd, dData, kData])

  function getMetricData(data: DataType) {
    const isDet = detFields.includes(type)
    return isDet ? getDetRowforDataset(data, ck) : getSegRowforDataset(data, type)
  }

  function generateDData(data: EvaluationResult) {
    const ddata: DataTypeForTable = Object.keys(data).reduce((prev, rid) => {
      const fiou = !ck && averageIou ? getAverageField(data[rid]) : getMetricData(data[rid])
      return {
        ...prev,
        [rid]: fiou,
      }
    }, {})
    setDData(ddata)
  }

  function generateKData(data: EvaluationResult) {
    const kdata: DataTypeForTable = {}
    Object.keys(data).forEach((id) => {
      const fiou = !ck && averageIou ? getAverageField(data[id]) : getMetricData(data[id])
      Object.keys(fiou).forEach((key) => {
        kdata[key] = kdata[key] || {}
        kdata[key][id] = fiou[key]
      })
    })
    setKData(kdata)
  }
  
  function generateDsItems() {
    return dd.map(({ value, label }) => ({ id: value, label, rows: generateDsRows(value) }))
  }

  function generateKwItems () {
    return kd.map(({ value, label }) => ({ id: value, label, rows: generateKwRows(value) }))
  }

  function generateDsRows(tid: number | string) {
    const tts = predictions.filter(({ inferDatasetId }) => inferDatasetId === tid)
    return tts.map((prediction) => {
      const rid = prediction.id
      const ddata = dData && dData[rid] ? dData[rid] : {}
      const kwAps = kd.reduce<{[key: string]: number}>((prev, { value: kw }) => {
        return {
          ...prev,
          [kw]: ddata[kw] ? ddata[kw][type] : 0,
        }
      }, {})
      const _average = average(Object.values(kwAps))
      const _model = getModelCell(prediction, models)
      return {
        id: rid,
        _model,
        _average,
        ...kwAps,
      }
    })
  }

  const generateKwRows = (kw: string | number) => {
    const kdata = kData && kData[kw] ? kData[kw] : {}
    const mids = [...new Set(predictions.map(({ inferModelId }) => inferModelId))]

    return mids
      .map(([mid, sid]) => {
        const preds = predictions.filter(({ inferModelId: [model, stage] }) => mid === model && sid === stage)
        const _model = getModelCell(preds[0], models)

        const drow = kdata
          ? preds.reduce((prev, { id, inferDatasetId }) => {
              const metric = kdata[id] ? kdata[id] : {}
              return {
                ...prev,
                [inferDatasetId]: metric[type],
              }
            }, {})
          : {}
        const _average = average(Object.values(drow))
        return {
          id: `${mid}${sid}`,
          config: preds[0]?.task?.config,
          _model,
          _average,
          ...drow,
        }
      })
      .flat()
  }

  function generateColumns() {
    const dynamicColumns = xasix.map(({ value, label }) => ({
      title: label,
      dataIndex: value,
      width: 100,
      render: percentRender,
    }))
    return [
      {
        title: 'Model',
        dataIndex: '_model',
        width: 150,
        ellipsis: true,
      },
      {
        title: t('common.average'),
        dataIndex: '_average',
        width: 100,
        render: percentRender,
      },
      ...dynamicColumns,
    ]
  }

  return (
    <>
      {list.map(({ id, label, rows }) => (
        <div key={id}>
          <Panel label={label} visible={!hiddens[id]} setVisible={(value) => setHiddens((old) => ({ ...old, [id]: !value }))} bg={false}>
            <Table
              dataSource={rows}
              rowKey={(record) => record.id}
              rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
              columns={columns}
              pagination={false}
              scroll={{ x: '100%' }}
            />
          </Panel>
        </div>
      ))}
    </>
  )
}

export default MapView
