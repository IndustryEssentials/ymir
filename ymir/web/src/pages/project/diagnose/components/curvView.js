import { useEffect, useState } from "react"
import { Col, Row, Table } from "antd"
import { percent } from '@/utils/number'

const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

const average = (nums = []) => nums.reduce((prev, num) => prev + num, 0) / nums.length

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
    const ddata = Object.keys(data).reduce((prev, id) => {
      const { iou_evaluations } = data[id]
      const fiou = Object.values(iou_evaluations)[0]
      return {
        ...prev,
        [id]: fiou[field],
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
          console.log('fiou[key]:', fiou[key])
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
    console.log('kd:', dd, kd, isDs)
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
    return tts.map(({ result: rid }) => {
      const ddata = kwType ? dData[rid][keywords].sub : dData[rid]
      console.log('ddata:', ddata)
      const kwAps = kd.reduce((prev, { value: kw }) => {
        return {
          ...prev,
          [kw]: ddata[kw].pr_curve,
        }
      }, {})
      const _model = getModelCell(rid)
      return {
        id: rid,
        _model,
        ...kwAps,
      }
    })
  }

  const generateKwRows = (kw) => {
    const kdata = kwType ? kData[keywords][kw] : kData[kw]
    const mids = [...new Set(tasks.map(({ model }) => model))]

    return mids.map(mid => {
      const tks = tasks.filter(({ model }) => model === mid)
      const _model = getModelCell(tks[0].result)
      const drow = tks.reduce((prev, { testing, result }) => {
        return {
          ...prev,
          [testing]: kdata[result].pr_curve
        }
      }, {})
      return {
        id: mid,
        _model,
        ...drow,
      }
    })
  }

  function getModelCell(rid) {
    const task = tasks.find(({ result }) => rid)
    const model = models.find(model => model.id === task.model)
    const stage = model.stages.find(sg => sg.id === task.stage)
    return <span title={JSON.stringify(task.config)}>{`${model.name} ${model.versionName} ${stage.name}`}</span>
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
      {columns.map(column => <Col>
        <h4>{column.label}</h4>
      {console.log('rows: ', rows)}
      </Col>
      )}
    </Row>
    {/* <Table
      dataSource={rows}
      rowKey={record => record.id}
      rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
      columns={columns}
      pagination={false}
    /> */}
  </div>)
}

export default CurveView
