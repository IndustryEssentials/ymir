import { useEffect, useState } from "react"
import { Col, Row, Table } from "antd"
import { percent } from '@/utils/number'
import { isSame } from '@/utils/object'
import Panel from "@/components/form/panel"
import { average, getCK, getKwField, getModelCell, opt, percentRender } from "./common"

// const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

// const average = (nums = []) => nums.reduce((prev, num) => !Number.isNaN(num) ? prev + num : prev, 0) / nums.length

// const getKwField = ({ iou_evaluations, iou_averaged_evaluation }, type) => !type ?
//   Object.values(iou_evaluations)[0]['ci_evaluations'] :
//   iou_averaged_evaluation['ck_evaluations']

const MapView = ({ tasks, datasets, models, data, xType, kw: { kwType, keywords } }) => {
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
    return tts.map(({ result: rid }) => {
      const ddata = (kwType ? dData[rid][keywords]?.sub : dData[rid]) || {}
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
    const kdata = kwType ? kData[keywords][kw] : kData[kw]

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
      const _average = kwType ? kdata._average?.ap : average(Object.values(drow))
      return {
        id: `${id}${rate}`,
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
        render: percentRender,
      },
      ...dynamicColumns,
    ]
  }

  // function getCK(data, keyword) {
  //   const cks = Object.values(data).map(({ iou_averaged_evaluation }) => {
  //     const ck = iou_averaged_evaluation.ck_evaluations[keyword] || {}
  //     return ck.sub ? Object.keys(ck.sub) : []
  //   }).flat()
  //   const uniqueCKs = [...new Set(cks)]
  //   return uniqueCKs.map(k => ({ value: k, label: k, parent: keywords }))
  // }

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
