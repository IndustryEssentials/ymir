import { useEffect, useState } from "react"
import { Table } from "antd"
import { percent, toFixed } from '@/utils/number'
import { isSame } from '@/utils/object'
import t from '@/utils/t'
import Panel from "@/components/form/panel"

const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

const average = (nums = []) => nums.reduce((prev, num) => !Number.isNaN(num) ? prev + num : prev, 0) / nums.length

const getKwField = ({ iou_evaluations, iou_averaged_evaluation }, type) => !type ?
  Object.values(iou_evaluations)[0]['ci_evaluations'] :
  iou_averaged_evaluation['ck_evaluations']

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
    return points?.reduce((prev, curr) =>
      Math.abs(prev[field] - value) <= Math.abs(curr[field] - value) ? prev : curr, 1)
  })
}
function findClosestPoint(target, points = [], field = 'x') {
  return points?.reduce((prev, curr) => Math.abs(prev[field] - target) <= Math.abs(curr[field] - target) ? prev : curr, 1)
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
  const [hiddens, setHiddens] = useState({})

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
        Object.keys(Object.values(data)[0].iou_averaged_evaluation.ck_evaluations[keywords].sub)
          .map(k => ({ value: k, label: k, parent: keywords })) :
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
  }, [xType, dd, kd, dData, kData, range])

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
    console.log('list:', list)
    setList(list)
  }

  function generateDsRows(tid) {
    const tts = tasks.filter(({ testing }) => testing === tid)

    return tts.map(({ model, result: rid }) => {
      return range.map(rate => {
        const ddata = kwType ? dData[rid][keywords].sub : dData[rid]

        const _model = getModelCell(rid)
        const kwPoints = kd.map(({ value: kw }) => {
          const line = ddata[kw]?.pr_curve
          return { point: findClosestPoint(rate, line, pointField[0]), kw }
        })
        const _average = average(kwPoints.map(({ point }) => point[pointField[1]]))
        const confidenceAverage = average(kwPoints.map(({ point: { z } }) => z))
        const kwFields = kwPoints.reduce((prev, { kw, point }) => ({
          ...prev,
          [`${kw}_target`]: point[pointField[1]],
          [`${kw}_conf`]: point.z,
        }), {})

        return {
          id: `${rid}${rate}`,
          value: rate,
          name: _model,
          ...kwFields,
          a: _average,
          ca: confidenceAverage,
        }
      })
    }).flat()
  }

  // todo
  function generateKwRows(kw) {
    const kdata = kwType ? kData[keywords][kw] : kData[kw]

    const mids = Object.values(tasks.reduce((prev, { model, stage, config }) => ({
      ...prev,
      [`${model}${stage}${JSON.stringify(config)}`]: { mid: model, sid: stage, config: config },
    }), {}))
    return mids.map(({ mid, sid, config }) => {
      const tts = tasks.filter(({ model, stage, config: tconfig }) => model === mid && stage === sid && isSame(config, tconfig))
      const _model = getModelCell(tts[0].result)

      return range.map(rate => {
        const points = tts.map(({ result: rid, testing: tid }) => {
          const line = kdata ? kdata[rid]?.pr_curve : []
          const point = findClosestPoint(rate, line, pointField[0])
          return {
            tid,
            point,
          }
        })
        const _average = average(points.map(({point}) => point[pointField[1]]))
        const confidenceAverage = average(points.map(({ point: { z }}) => z))
        const tpoints = points.reduce((prev, { tid, point }) => ({
          ...prev,
          [`${tid}_target`]: point[pointField[1]],
          [`${tid}_conf`]: point.z,
        }), {})

        return {
          
            id: `${mid}${sid}${JSON.stringify(config)}${rate}`,
            value: rate,
            name: _model,
            ...tpoints,
            a: _average,
            ca: confidenceAverage,
        }
      })
    }).flat()
  }

  function getModelCell(rid) {
    const task = tasks.find(({ result }) => result === rid)
    const model = models.find(model => model.id === task.model)
    const stage = model.stages.find(sg => sg.id === task.stage)
    return <span title={JSON.stringify(task.config)}>{`${model.name} ${model.versionName} ${stage.name}`}</span>
  }

  function generateColumns() {
    const dynamicColumns = xasix.map(({ value, label }) => ([
      {
        title: t(labels.colTarget, { label: <div>{label}</div> }),
        dataIndex: `${value}_target`,
        colSpan: 2,
        render: percentRender,
      }, {
        title: t('model.diagnose.metrics.confidence.label', { label }),
        colSpan: 0,
        dataIndex: `${value}_conf`,
        render: percentRender,
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
        render: percentRender,
      },
    ]
  }

  const percentRender = value => typeof value === 'number' && !Number.isNaN(value) ? percent(value) : '-'

  return list.map(({ id, label, rows }) => <div key={id}>
    <Panel label={label} visible={!hiddens[id]} setVisible={value => setHiddens(old => ({ ...old, [id]: !value }))} bg={false}>
      <Table
        dataSource={rows}
        rowKey={record => record.id}
        rowClassName={(record, index) => Math.floor(index / range.length) % 2 === 0 ? '' : 'oddRow'}
        columns={columns}
        pagination={false}
        scroll={{ x: '100%' }}
      />
    </Panel>
  </div>)
}

export default PView
