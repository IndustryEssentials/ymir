import { useCallback, useEffect, useState } from "react"
import { Table } from "antd"
import { percent } from '@/utils/number'

const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

const average = (nums = []) => nums.reduce((prev, num) => prev + num, 0) / nums.length

const getKwField = type => !type ? 'ci_evaluations' : 'ck_evaluations'

const MapView = ({ tasks, datasets, models, data, xType, kwType, keywords }) => {
  const [list, setList] = useState([])
  const [dd, setDD] = useState([])
  const [kd, setKD] = useState([])
  const [xasix, setXAsix] = useState([])
  const [dData, setDData] = useState(null)
  const [kData, setKData] = useState(null)
  const [columns, setColumns] = useState([])

  useEffect(() => {
    if (data) {
      generateDData(data)
      generateKData(data)
    }
  }, [data])

  useEffect(() => {
    setDD(datasets.map(opt))
  }, [datasets])

  useEffect(() => {
    setKD(keywords.map(k => ({ value: k, label: k })))
  }, [keywords])

  useEffect(() => {
    const cls = generateColumns()
    console.log('cls:', cls)
    setColumns(cls)
  }, [xasix])

  useEffect(() => {
    // list
    if (dData && kData) {
      const isDs = xType === 'dataset'
      generateList(isDs)
      setXAsix(isDs ? kd : dd)
    }
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
        const item = fiou[key]
        kdata[key][id] = item.sub || item
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
    console.log('list:', list)
    setList(list)
  }

  function generateDsRows(tid) {
    const tts = tasks.filter(({ testing }) => testing === tid)
    return tts.map(({ result: rid }) => {
      const ddata = dData[rid]
      console.log('ddata:', ddata)
      const kwAps = Object.keys(ddata).reduce((prev, kw) => {
        return {
          ...prev,
          [kw]: ddata[kw].ap,
        }
      }, {})
      const _average = average(Object.values(kwAps))
      const _model = getModelCell(rid)
      return {
        _model,
        _average,
        ...kwAps,
      }
    })
  }

  const generateKwRows = (kw) => {
    const kdata = kData[kw]
    console.log('kdata:', kdata)
    const mids = [...new Set(tasks.map(({ model }) => model))]

    return mids.map(mid => {
      const tks = tasks.filter(({ model }) => model === mid)
      const _model = getModelCell(tks[0].result)
      const drow = tks.reduce((prev, { testing, result }) => {
        return {
          ...prev,
          [testing]: kdata[result].ap
        }
      }, {})
      const _average = average(Object.values(drow))
      return {
        _model,
        _average,
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
    <Table
      dataSource={rows}
      rowKey={(record, index) => index}
      rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
      columns={columns}
      pagination={false}
    />
  </div>)
}

export default MapView
