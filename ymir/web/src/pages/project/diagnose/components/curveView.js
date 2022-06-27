import { useEffect, useState } from "react"
import { Col, Row, Table } from "antd"
import { percent } from '@/utils/number'
import PrCurve from "./prCurve"

const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

const getKwField = type => !type ? 'ci_evaluations' : 'ck_evaluations'

const CurveView = ({ tasks, datasets, models, data, filter: { xType, kwType, keywords } }) => {
  const [list, setList] = useState([])
  const [dd, setDD] = useState([])
  const [kd, setKD] = useState([])
  const [xasix, setXAsix] = useState([])
  const [dData, setDData] = useState(null)
  const [kData, setKData] = useState(null)
  const [columns, setColumns] = useState([])

  useEffect(() => {
    if (data && keywords) {
      generateDData(data)
      generateKData(data)
    } else {
      setDData(null)
      setKData(null)
    }
  }, [kwType, data, keywords])

  useEffect(() => {
    setDD(datasets.map(opt))
  }, [datasets])

  useEffect(() => {
    console.log('data && keywords:', data, keywords, kwType)
    if (data && keywords) {
      const kws = kwType ?
        Object.keys(Object.values(Object.values(data)[0].iou_evaluations)[0].ck_evaluations[keywords].sub)
          .map(k => ({ value: k, label: k, parent: keywords })) :
        keywords.map(k => ({ value: k, label: k }))
      setKD(kws)
    }
  }, [keywords, data, kwType])

  useEffect(() => {
    const cls = generateColumns()
    console.log('cls:', cls)
    setColumns(cls)
  }, [xasix])

  useEffect(() => {
    // list
    if (dData && kData) {
      generateList(!xType)
      setXAsix(xType ? dd : kd)
    } else {
      setList([])
    }
    console.log('xType, dd, kd, dData, kData:', xType, dd, kd, dData, kData)
  }, [xType, dd, kd, dData, kData])

  function generateDData(data) {

    const field = getKwField(kwType)
    const ddata = Object.keys(data).reduce((prev, rid) => {
      const { iou_evaluations } = data[rid]
      const fiou = Object.values(iou_evaluations)[0]
      return {
        ...prev,
        [rid]: fiou[field],
      }
    }, {})
    setDData(ddata)
  }

  function generateKData(data) {
    const field = getKwField(kwType)
    const kdata = {}
    Object.keys(data).forEach(id => {
      const { iou_evaluations } = data[id]
      const fiou = Object.values(iou_evaluations)[0][field]
      Object.keys(fiou).forEach(key => {
        kdata[key] = kdata[key] || {}
        if (kwType) {
          Object.keys(fiou[key].sub).forEach(subKey => {
            kdata[key][subKey] = kdata[key][subKey] || { _average: fiou[key].total }
            kdata[key][subKey][id] = fiou[key].sub[subKey]
          })
        } else {
          kdata[key][id] = fiou[key]
        }
      })
    })
    console.log('kdata:', kdata)
    setKData(kdata)
  }

  function generateList(isDs) {
    const titles = isDs ? dd : kd
    const list = titles.map(({ value, label }) => ({
      id: value, label,
      rows: isDs ? generateDsRows(value) : generateKwRows(value),
    }))
    console.log('list:', list)
    setList(list)
  }

  function generateDsRows(tid) {
    const tts = tasks.filter(({ testing }) => testing === tid)

    return kd.map(({ value }) => {
      const kwRows = tts.map(({ result: rid }) => {
        const ddata = kwType ? dData[rid][keywords].sub : dData[rid]
        const _model = getModelCell(rid)
        const line = ddata[value].pr_curve
        return {
          id: rid,
          name: _model,
          line,
        }
      })
      return {
        id: value,
        title: value,
        lines: kwRows,
      }
    })
  }

  const generateKwRows = (kw) => {
    const kdata = kwType ? kData[keywords][kw] : kData[kw]

    return dd.map(({ value: tid, label }) => {
      const tks = tasks.filter(({ testing }) => testing === tid)
      const lines = tks.map(({ testing, result }) => {
        const _model = getModelCell(result)
        return {
          id: testing,
          name: _model,
          line: kdata[result].pr_curve
        }
      })
      return {
        id: tid,
        title: label,
        lines,
      }
    })
  }

  function getModelCell(rid) {
    const task = tasks.find(({ result }) => result === rid)
    const model = models.find(model => model.id === task.model)
    const stage = model.stages.find(sg => sg.id === task.stage)
    return `${model.name} ${model.versionName} ${stage.name}`
  }

  function generateColumns() {
    const dynamicColumns = xasix.map(({ value, label }) => ({
      title: label,
      dataIndex: value,
      render: mapRender,
    }))
    return [
      {
        title: 'Model',
        dataIndex: '_model',
      },
      {
        title: 'Average AP',
        dataIndex: '_average',
        render: mapRender,
      },
      ...dynamicColumns,
    ]
  }

  const mapRender = value => {
    const ap = value?.ap || value
    return !Number.isNaN(ap) ? percent(ap) : '-'
  }

  return list.map(({ id, label, rows }) => <div key={id}>
    <h3>{label}</h3>
    <Row gutter={20}>
      {rows.map(({ id, title, lines }, index) => <Col key={id} flex={1}>
        <h4>{columns[index].label}</h4>
        <PrCurve title={title} lines={lines} />
      </Col>
      )}
    </Row>
  </div>)
}

export default CurveView
