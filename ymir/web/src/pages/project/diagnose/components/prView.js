import { useEffect, useState } from "react"
import { Table } from "antd"
import { percent, toFixed } from '@/utils/number'
import t from '@/utils/t'

const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

const average = (nums = []) => nums.reduce((prev, num) => prev + num, 0) / nums.length

const getKwField = type => !type ? 'ci_evaluations' : 'ck_evaluations'

const getLabels = type => ({
  colMain: `model.diagnose.metrics.${type}.label`,
  colAverage: `model.diagnose.metrics.${type}.average.label`,
  colTarget: `model.diagnose.metrics.${type}.target.label`,
})


function generateRange(min, max, step = 0.05) {
  let result = []
  let current = min * 100
  while (current <= max * 100) {
    result.push(current / 100)
    current += step * 100
  }
  return result
}

function rangePoints(range, points = [], field = 'x') {
  return range.map(value => {
    return points.reduce((prev, curr) =>
      Math.abs(prev[field] - value) <= Math.abs(curr[field] - value) ? prev : curr, 1)
  })
}

const PView = ({ tasks, datasets, models, data, prType, prRate, xType, kw: { kwType, keywords } }) => {
  const [list, setList] = useState([])
  const [dd, setDD] = useState([])
  const [kd, setKD] = useState([])
  const [xasix, setXAsix] = useState([])
  const [dData, setDData] = useState(null)
  const [kData, setKData] = useState(null)
  const [columns, setColumns] = useState([])
  const [range, setRange] = useState([])
  const [pointField, setPointField] = useState(['x', 'y'])
  const [labels, setLabels] = useState({})

  useEffect(() => {
    const min = prRate[0]
    const max = prRate[1]
    setRange(generateRange(min, max))
  }, [prRate])

  useEffect(() => {
    setPointField(prType ? ['y', 'x'] : ['x', 'y'])
    setLabels(getLabels(prType ? 'recall' : 'precision'))
  }, [prType])

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
  }, [xType, dd, kd, dData, kData, range])

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
    console.log('list:', list)
    setList(list)
  }

  function generateDsRows(tid) {
    const tts = tasks.filter(({ testing }) => testing === tid)

    return kd.map(({ value }) => {
      return tts.map(({ model, result: rid }) => {
        const ddata = kwType ? dData[rid][keywords].sub : dData[rid]
        const _model = getModelCell(rid)
        const line = ddata[value].pr_curve
        const points = rangePoints(range, line, pointField[0])
        const recallAverage = toFixed(average(points.map(point => point[pointField[1]])), 4)
        const confidenceAverage = toFixed(average(points.map(({ z }) => z)))
        return points.map((point, index) => ({
          id: `${rid}${range[index]}`,
          value: range[index],
          span: model,
          title: value,
          name: _model,
          target: point[pointField[1]],
          point,
          conf: point.z,
          a: recallAverage,
          ca: confidenceAverage,
        })).flat()
      }).flat()
    }).flat()
  }

  function generateKwRows(kw) {
    const kdata = kwType ? kData[keywords][kw] : kData[kw]

    return dd.map(({ value: tid, label }) => {
      const tks = tasks.filter(({ testing }) => testing === tid)
      return tks.map(({ model, result }) => {
        const _model = getModelCell(result)
        const line = kdata[result].pr_curve
        const points = rangePoints(range, line, pointField[0])
        const recallAverage = toFixed(average(points.map(point => point[pointField[1]])), 4)
        const confidenceAverage = toFixed(average(points.map(({ z }) => z)))
        return points.map((point, index) => ({
          id: `${result}${range[index]}`,
          value: range[index],
          span: model,
          title: label,
          name: _model,
          target: point[pointField[1]],
          point,
          conf: point.z,
          a: recallAverage,
          ca: confidenceAverage,
        })).flat()
      }).flat()
    }).flat()
  }

  function getModelCell(rid) {
    const task = tasks.find(({ result }) => result === rid)
    const model = models.find(model => model.id === task.model)
    const stage = model.stages.find(sg => sg.id === task.stage)
    return <span title={JSON.stringify(task.config)}>{`${model.name} ${model.versionName} ${stage.name}`}</span>
  }

  function generateColumns() {
    console.log('labels:', labels)
    const dynamicColumns = xasix.map(({ value, label }) => ([
      {
        title: t(labels.colTarget, { label }),
        dataIndex: value,
        render: (_, record) => percent(record.target),
      }, {
        title: t('model.diagnose.metrics.confidence.label', { label }),
        dataIndex: value,
        render: (_, { conf }) => conf,
      },
    ])).flat()
    return [
      {
        title: 'Model',
        dataIndex: 'name',
        onCell: (_, index) => ({
          rowSpan: index % range.length ? 0 : range.length,
        }),
      },
      {
        title: t(labels.colMain),
        dataIndex: 'value',
        render: percentRender,
      },
      ...dynamicColumns,
      {
        title: t(labels.colAverage),
        dataIndex: 'a',
        render: percentRender,
      },
      {
        title: t('model.diagnose.metrics.confidence.average.label'),
        dataIndex: 'ca',
      },
    ]
  }

  const percentRender = value => !Number.isNaN(value) ? percent(value) : '-'

  return list.map(({ id, label, rows }) => <div key={id}>
    <h3>{label}</h3>
    <Table
      dataSource={rows}
      rowKey={record => record.id}
      rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
      columns={columns}
      pagination={false}
    />
  </div>)
}

export default PView
