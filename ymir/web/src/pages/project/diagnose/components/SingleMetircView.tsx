import { FC, ReactNode, useEffect, useState } from 'react'
import { Col, Row, Table, TableColumnsType } from 'antd'
import { percent } from '@/utils/number'
import { isSame } from '@/utils/object'
import Panel from '@/components/form/panel'
import {
  average,
  DataType,
  getAverageField,
  getCK,
  getDetRowforDataset,
  getKwField,
  getModelCell,
  getSegRowforDataset,
  MetricType,
  opt,
  percentRender,
  ViewProps,
} from './common'
import type { Task } from './common'
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

type DatasetDataType = {
  [id: number | string]: {
    [keyword: string]: MetricType
  }
}

type ClassesDataType = {
  [keyword: string]: {
    [id: number | string]: MetricType
  }
}

const detFields = ['ap', 'maskap', 'boxap']

const MapView: FC<ViewProps> = ({ type, tasks, datasets, models, data, xByClasses, kw: { ck, keywords }, averageIou }) => {
  const [list, setList] = useState<ListType[]>([])
  const [dd, setDD] = useState<KeywordType[]>([])
  const [kd, setKD] = useState<KeywordType[]>([])
  const [xasix, setXAsix] = useState<KeywordType[]>([])
  const [dData, setDData] = useState<DatasetDataType>()
  const [kData, setKData] = useState<ClassesDataType>()
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
      generateList(!xByClasses)
      setXAsix(xByClasses ? dd : kd)
    } else {
      setList([])
    }
  }, [xByClasses, dd, kd, dData, kData])

  function getMetricData(data: DataType) {
    const isDet = detFields.includes(type)
    return isDet ? getDetRowforDataset(data, ck) : getSegRowforDataset(data, type)
  }

  function generateDData(data: any) {
    const ddata: DatasetDataType = Object.keys(data).reduce((prev, rid) => {
      const fiou = !ck && averageIou ? getAverageField(data[rid]) : getMetricData(data[rid])
      console.log('fiou:', fiou, ck, averageIou)
      return {
        ...prev,
        [rid]: fiou,
      }
    }, {})
    setDData(ddata)
  }

  function generateKData(data: any) {
    const kdata: ClassesDataType = {}
    Object.keys(data).forEach((id) => {
      const fiou = !ck && averageIou ? getAverageField(data[id]) : getMetricData(data[id])
      Object.keys(fiou).forEach((key) => {
        kdata[key] = kdata[key] || {}
        kdata[key][id] = fiou[key]
      })
    })
    setKData(kdata)
  }

  function generateList(isDs: boolean) {
    const titles = isDs ? dd : kd
    const list = titles.map(({ value, label }) => ({
      id: value,
      label,
      rows: isDs ? generateDsRows(value) : generateKwRows(value),
    }))
    setList(list)
  }

  function generateDsRows(tid: number | string) {
    const tts = tasks.filter(({ testing }) => testing === tid)
    return tts.map(({ result: rid }) => {
      const ddata = dData && dData[rid] ? dData[rid] : {}
      const kwAps = kd.reduce((prev, { value: kw }) => {
        const metric = ddata[kw] ? ddata[kw][type] : null
        return {
          ...prev,
          [kw]: metric,
        }
      }, {})
      const _average = average(Object.values(kwAps))
      const _model = getModelCell(rid, tasks, models)
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

    const mids: { id: number; mid: number; sid: number; config: { [key: string]: any } }[] = Object.values(
      tasks.reduce((prev, { model, stage, config }) => {
        const id = `${model}${stage}${JSON.stringify(config)}`
        return {
          ...prev,
          [id]: { id, mid: model, sid: stage, config: config },
        }
      }, {}),
    )

    return mids
      .map(({ id, mid, sid, config }) => {
        const tts = tasks.filter(({ model, stage, config: tconfig }) => model === mid && stage === sid && isSame(config, tconfig))
        const _model = getModelCell(tts[0].result, tasks, models)

        const drow = kdata
          ? tts.reduce((prev, { testing, result }) => {
              const metric = kdata[result] ? kdata[result][type] : null
              return {
                ...prev,
                [testing]: metric,
              }
            }, {})
          : {}
        const _average = average(Object.values(drow))
        return {
          id,
          config,
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
