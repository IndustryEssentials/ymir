import { useEffect, useState } from "react"
import { Col, Row, Table } from "antd"
import PrCurve from "./prCurve"
import { getCK, getKwField, getModelCell, opt } from "./common"

const CurveView = ({ tasks, datasets, models, data, xType, kw: { kwType, keywords } }) => {
  const [list, setList] = useState([])
  const [dd, setDD] = useState([])
  const [kd, setKD] = useState([])
  const [xasix, setXAsix] = useState([])
  const [dData, setDData] = useState(null)
  const [kData, setKData] = useState(null)

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
    if (data && keywords) {
      const kws = kwType ?
        getCK(data, keywords) :
        keywords.map(k => ({ value: k, label: k }))
      setKD(kws)
    }
  }, [keywords, data, kwType])

  useEffect(() => {
    // list
    if (dData && kData) {
      generateList(!xType)
      setXAsix(xType ? dd : kd)
    } else {
      setList([])
    }
  }, [xType, dd, kd, dData, kData])

  function generateDData(data) {
    const ddata = Object.keys(data).reduce((prev, rid) => {
      const fiou = getKwField(data[rid], kwType)
      return {
        ...prev,
        [rid]: fiou,
      }
    }, {})
    setDData(ddata)
  }

  function generateKData(data) {
    const kdata = {}
    Object.keys(data).forEach(id => {
      const fiou = getKwField(data[id], kwType)
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
    setKData(kdata)
  }

  function generateList(isDs) {
    const titles = isDs ? dd : kd
    const list = titles.map(({ value, label }) => ({
      id: value, label,
      rows: isDs ? generateDsRows(value) : generateKwRows(value),
    }))
    setList(list)
  }

  function generateDsRows(tid) {
    const tts = tasks.filter(({ testing }) => testing === tid)

    return kd.map(({ value }) => {
      const kwRows = tts.map(({ result: rid }) => {
        const ddata = (kwType ? dData[rid][keywords]?.sub : dData[rid]) || {}
        const _model = getModelCell(rid, tasks, models)
        const line = ddata[value]?.pr_curve || []
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
    const kdata = kwType ? (kData[keywords] ? kData[keywords][kw] : null) : kData[kw]

    return dd.map(({ value: tid, label }) => {
      const tks = tasks.filter(({ testing }) => testing === tid)
      const lines = tks.map(({ testing, result }) => {
        const _model = getModelCell(result, tasks, models)
        return {
          id: testing,
          name: _model,
          line: kdata ? kdata[result]?.pr_curve : [],
        }
      })
      return {
        id: tid,
        title: label,
        lines,
      }
    })
  }

  return list.map(({ id, label, rows }) => <div key={id}>
    <h3>{label}</h3>
    <Row gutter={20}>
      {rows.map(({ id, title, lines }, index) => <Col key={id} flex={1} style={{ minWidth: 200 }}>
        <PrCurve title={title} lines={lines} />
      </Col>
      )}
    </Row>
  </div>)
}

export default CurveView
