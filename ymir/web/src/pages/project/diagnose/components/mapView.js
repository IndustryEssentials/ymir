import { useEffect, useState } from "react"
import { Col, Row, Table } from "antd"
import { percent } from '@/utils/number'
import { isSame } from '@/utils/object'
import Panel from "@/components/form/panel"
import { average, getAverageField, getCK, getKwField, getModelCell, opt, percentRender } from "./common"

const MapView = ({ tasks, datasets, models, data, xType, kw: { kwType, keywords }, averageIou }) => {
  const [list, setList] = useState([])
  const [dd, setDD] = useState([])
  const [kd, setKD] = useState([])
  const [xasix, setXAsix] = useState([])
  const [dData, setDData] = useState(null)
  const [kData, setKData] = useState(null)
  const [columns, setColumns] = useState([])
  const [hiddens, setHiddens] = useState({})

  useEffect(() => {
    if (data && keywords) {
      generateDData(data)
      generateKData(data)
    } else {
      setDData(null)
      setKData(null)
    }
  }, [kwType, data, keywords, averageIou])

  useEffect(() => {
    setDD(datasets.map(opt))
  }, [datasets])

  useEffect(() => {
    if (data && keywords) {
      const kws = keywords.map(k => ({ value: k, label: k }))
      setKD(kws)
    }
  }, [keywords, data, kwType])

  useEffect(() => {
    const cls = generateColumns()
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
  }, [xType, dd, kd, dData, kData])

  function generateDData(data) {
    const ddata = Object.keys(data).reduce((prev, rid) => {
      const fiou = (!kwType && averageIou) ? getAverageField(data[rid]) : getKwField(data[rid], kwType)
      console.log('fiou:', fiou, averageIou)
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
      const fiou = (!kwType && averageIou) ? getAverageField(data[id]) : getKwField(data[id], kwType)
      console.log('generateKData fiou:', fiou)
      Object.keys(fiou).forEach(key => {
        kdata[key] = kdata[key] || {}
        kdata[key][id] = fiou[key]
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
    return tts.map(({ result: rid }) => {
      const ddata = dData[rid] || {}
      const kwAps = kd.reduce((prev, { value: kw }) => {
        return {
          ...prev,
          [kw]: ddata[kw]?.ap,
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

  const generateKwRows = (kw) => {
    const kdata = kData[kw]

    const mids = Object.values(tasks.reduce((prev, { model, stage, config }) => {
      const id = `${model}${stage}${JSON.stringify(config)}`
      return {
        ...prev,
        [id]: { id, mid: model, sid: stage, config: config },
      }
    }, {}))

    return mids.map(({ id, mid, sid, config }) => {
      const tts = tasks.filter(({ model, stage, config: tconfig }) => model === mid && stage === sid && isSame(config, tconfig))
      const _model = getModelCell(tts[0].result, tasks, models)

      const drow = kdata ? tts.reduce((prev, { testing, result }) => {
        return {
          ...prev,
          [testing]: kdata[result]?.ap,
        }
      }, {}) : {}
      const _average = average(Object.values(drow))
      return {
        id,
        config,
        _model,
        _average,
        ...drow,
      }
    }).flat()
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
        title: 'Average mAP',
        dataIndex: '_average',
        width: 100,
        render: percentRender,
      },
      ...dynamicColumns,
    ]
  }

  return list.map(({ id, label, rows }) => <div key={id}>
    <Panel label={label} visible={!hiddens[id]} setVisible={value => setHiddens(old => ({ ...old, [id]: !value }))} bg={false}>
      <Table
        dataSource={rows}
        rowKey={record => record.id}
        rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
        columns={columns}
        pagination={false}
        scroll={{ x: '100%' }}
      />
    </Panel>
  </div>)
}

export default MapView
