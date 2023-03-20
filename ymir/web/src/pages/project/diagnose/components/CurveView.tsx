import { FC, useEffect, useState } from 'react'
import { Col, Row, Table } from 'antd'
import PrCurve from './PRCurve'
import Panel from '@/components/form/panel'
import { getKwField, getModelCell, opt } from './common'
import { ChartDataType, DataTypeForTable, EvaluationResult, ListType, OptionType, ViewProps } from '.'

const CurveView: FC<ViewProps> = ({ predictions, datasets, models, data, xByClasses, kw: { ck, keywords } }) => {
  const [list, setList] = useState<ListType<ChartDataType>>([])
  const [dd, setDD] = useState<OptionType<number>[]>([])
  const [kd, setKD] = useState<OptionType[]>([])
  const [dData, setDData] = useState<DataTypeForTable>()
  const [kData, setKData] = useState<DataTypeForTable>()
  const [hiddens, setHiddens] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    if (data && keywords) {
      generateDData(data)
      generateKData(data)
    } else {
      setDData(undefined)
      setKData(undefined)
    }
  }, [data, keywords])

  useEffect(() => {
    setDD(datasets.map(opt))
  }, [datasets])

  useEffect(() => {
    if (data && keywords) {
      const kws = keywords.map((k) => ({ value: k, label: k }))
      setKD(kws)
    }
  }, [keywords, data])

  useEffect(() => {
    // list
    if (dData && kData) {
      setList(xByClasses ? generateKwItems() : generateDsItems())
    } else {
      setList([])
    }
  }, [xByClasses, dd, kd, dData, kData])

  function generateDData(data: EvaluationResult) {
    const ddata = Object.keys(data).reduce<DataTypeForTable>((prev, rid) => {
      const fiou = getKwField(data[rid], ck)
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
      const fiou = getKwField(data[id], ck)
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

    return kd.map(({ value }) => {
      const kwRows = tts.map((prediction) => {
        const rid = prediction.id
        const ddata = dData && dData[rid] ? dData[rid] : {}
        const _model = getModelCell(prediction, models, 'text')
        const line = ddata[value]?.pr_curve || []
        return {
          id: rid,
          name: _model,
          line,
        }
      })
      return {
        id: value,
        title: `${value}`,
        lines: kwRows,
      }
    })
  }

  const generateKwRows = (kw: string | number) => {
    const kdata = kData && kData[kw] ? kData[kw] : {}
    const mids = [...new Set(predictions.map(({ inferModelId }) => inferModelId))]
    return dd.map(({ value: tid, label }) => {
      const tks = predictions.filter(({ inferDatasetId }) => inferDatasetId === tid)
      const lines = tks.map((prediction) => {
        const id = prediction.id
        const _model = getModelCell(prediction, models, 'text')
        return {
          id,
          name: _model,
          line: kdata ? kdata[id]?.pr_curve : [],
        }
      })
      return {
        id: tid,
        title: label,
        lines,
      }
    })
  }

  return (
    <div>
      {list.map(({ id, label, rows }) => (
        <Panel key={id} label={label} visible={!hiddens[id]} setVisible={(value) => setHiddens((old) => ({ ...old, [id]: !value }))} bg={false}>
          <Row gutter={20}>
            {rows.map(({ id, title, lines }, index) => (
              <Col key={id} span={24} style={{ minWidth: 300 }}>
                <PrCurve title={title} lines={lines} />
              </Col>
            ))}
          </Row>
        </Panel>
      ))}
    </div>
  )
}

export default CurveView
