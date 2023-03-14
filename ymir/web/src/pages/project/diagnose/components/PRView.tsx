import { FC, useEffect, useState } from 'react'
import { Table, TableColumnsType } from 'antd'
import { percent, toFixed } from '@/utils/number'
import { isSame } from '@/utils/object'
import t from '@/utils/t'
import Panel from '@/components/form/panel'
import { average, getCK, getKwField, opt, percentRender, getModelCell, confidenceRender } from './common'
import { DataTypeForTable, EvaluationResult, ListType, MetricsType, OptionType, Point, TableDataType, ViewProps } from '.'

const getLabels = (type: string) => ({
  colMain: `model.diagnose.metrics.${type}.label`,
  colAverage: `model.diagnose.metrics.${type}.average.label`,
  colTarget: `model.diagnose.metrics.${type}.target.label`,
})

function generateRange(min: number, max: number, step = 0.05) {
  let result = []
  let current = min * 100
  while (current <= max * 100) {
    result.push(current / 100)
    current += step * 100
  }
  return result
}

function findClosestPoint(target: number, points: Point[] = [], field: keyof Point = 'x') {
  return points?.reduce((prev, curr) => (Math.abs(prev[field] - target) <= Math.abs(curr[field] - target) ? prev : curr), { [field]: 1 })
}

const PView: FC<ViewProps> = ({ predictions, datasets, models, data, p2r, prRate, xByClasses, kw: { ck, keywords } }) => {
  const [list, setList] = useState<ListType>([])
  const [dd, setDD] = useState<OptionType<number>[]>([])
  const [kd, setKD] = useState<OptionType[]>([])
  const [xasix, setXAsix] = useState<OptionType<string | number>[]>([])
  const [dData, setDData] = useState<DataTypeForTable | null>(null)
  const [kData, setKData] = useState<DataTypeForTable | null>(null)
  const [columns, setColumns] = useState<TableColumnsType<TableDataType>>([])
  const [range, setRange] = useState<number[]>([])
  const [pointField, setPointField] = useState<(keyof Point)[]>(['x', 'y'])
  const [labels, setLabels] = useState<ReturnType<typeof getLabels>>()
  const [hiddens, setHiddens] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    if (!prRate) {
      return
    }
    const min = prRate[0]
    const max = prRate[1]
    setRange(generateRange(min, max))
  }, [prRate])

  useEffect(() => {
    setPointField(p2r ? ['y', 'x'] : ['x', 'y'])
    setLabels(getLabels(p2r ? 'recall' : 'precision'))
  }, [p2r])

  useEffect(() => {
    if (data && keywords) {
      generateDData(data)
      generateKData(data)
    } else {
      setDData(null)
      setKData(null)
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
    const cls = generateColumns()
    setColumns(cls)
  }, [xasix])

  useEffect(() => {
    // list
    if (dData && kData) {
      setList(xByClasses ? generateKwItems() : generateDsItems())
      setXAsix(xByClasses ? dd : kd)
    } else {
      setList([])
    }
  }, [xByClasses, dd, kd, dData, kData, range])

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

  function generateDsRows(tid: number): TableDataType[] {
    const tts = predictions.filter(({ inferDatasetId }) => inferDatasetId === tid)

    return tts
      .map((prediction) => {
        const id = prediction.id
        return range.map((rate) => {
          const ddata = dData && dData[id] ? dData[id] : {}

          const _model = getModelCell(prediction, models)
          const kwPoints = kd.map(({ value: kw }) => {
            const line: Point[] = ddata[kw]?.pr_curve || []
            return { point: findClosestPoint(rate, line, pointField[0]), kw }
          })
          const _average = average(kwPoints.map(({ point }) => point[pointField[1]]))
          const confidenceAverage = average(kwPoints.map(({ point: { z } }) => z))
          const kwFields = kwPoints.reduce(
            (prev, { kw, point }) => ({
              ...prev,
              [`${kw}_target`]: point[pointField[1]],
              [`${kw}_conf`]: point.z,
            }),
            {},
          )

          return {
            id: `${id}${rate}`,
            value: rate,
            name: _model,
            ...kwFields,
            a: _average,
            ca: confidenceAverage,
          }
        })
      })
      .flat()
  }

  function generateKwRows(kw: string): TableDataType[] {
    const kdata = kData && kData[kw] ? kData[kw] : {}

    const mids = [...new Set(predictions.map(({ inferModelId }) => inferModelId))]
    const cols = predictions.map(({ inferDatasetId }) => inferDatasetId)

    return mids
      .map(([mid, sid]) => {
        const preds = predictions.filter(({ inferModelId: [model, stage] }) => mid === model && sid === stage)

        // const { id, inferModelId: [mid, sid], task: { config } = {config: {}} } = prediction
        // const tts = tasks.filter(({ model, stage, config: tconfig }) => model === mid && stage === sid && isSame(config, tconfig))
        const _model = getModelCell(preds[0], models)

        return range.map((rate) => {
          const points = preds.map(({ inferDatasetId: tid }) => {
            const line = kdata[tid]?.pr_curve || []
            const point = findClosestPoint(rate, line, pointField[0])
            return {
              tid,
              point,
            }
          })
          const _average = average(points.map(({ point }) => point[pointField[1]]))
          const confidenceAverage = average(points.map(({ point: { z } }) => z))
          const tpoints = points.reduce(
            (prev, { tid, point }) => ({
              ...prev,
              [`${tid}_target`]: point[pointField[1]],
              [`${tid}_conf`]: point.z,
            }),
            {},
          )

          return {
            id: `${mid}${rate}`,
            value: rate,
            name: _model,
            ...tpoints,
            a: _average,
            ca: confidenceAverage,
          }
        })
      })
      .flat()
  }

  function generateColumns(): TableColumnsType<TableDataType> {
    const dynamicColumns = xasix
      .map(({ value, label }) => [
        {
          title: t(labels?.colTarget, { label: <div>{label}</div> }),
          dataIndex: `${value}_target`,
          colSpan: 2,
          width: 100,
          render: percentRender,
        },
        {
          colSpan: 0,
          dataIndex: `${value}_conf`,
          width: 100,
          render: confidenceRender,
        },
      ])
      .flat()
    return [
      {
        title: 'Model',
        dataIndex: 'name',
        width: 150,
        onCell: (_, index: number = 0) => ({
          rowSpan: index % range.length ? 0 : range.length,
        }),
      },
      {
        title: t(labels?.colMain),
        dataIndex: 'value',
        width: 100,
        render: percentRender,
      },
      ...dynamicColumns,
      {
        title: t(labels?.colAverage),
        dataIndex: 'a',
        width: 100,
        render: percentRender,
      },
      {
        title: t('model.diagnose.metrics.confidence.average.label'),
        dataIndex: 'ca',
        width: 100,
        render: confidenceRender,
      },
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
              rowClassName={(record, index) => (Math.floor(index / range.length) % 2 === 0 ? '' : 'oddRow')}
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

export default PView
