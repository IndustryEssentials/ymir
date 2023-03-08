import LineChart from '@/components/chart/line'
import { useEffect, useState } from 'react'
import { Card } from 'antd'

import Empty from '@/components/empty/default'

const PrCurve = ({ title = '', lines }) => {
  const [option, setOption] = useState({})
  const [series, setSeries] = useState([])
  const [xasix, setXAsix] = useState([])
  const tooltip = {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow',
    },
  }

  const legend = {}
  const grid = {
    left: 20,
    right: 20,
    containLabel: true,
  }
  const yAxis = [
    {
      type: 'value',
      name: 'Precision',
      nameLocation: 'center',
      nameGap: 30,
    },
  ]

  useEffect(() => {
    if (!lines.length) {
      return
    }
    const series = lines.map(({ name, line }) => {
      return {
        symbol: 'circle',
        symbolSize: 2,
        type: 'scatter',
        data: line.map(({ x, y }) => [x, y]),
        markLine: {
          symbol: 'circle',
          
          lineStyle: {
            type: 'solid',
            width: 2,
          },
          data: line.reduce((prev, { x, y }, index) => {
            const next = line[index + 1]
            return next ? [...prev, [{ coord: [x, y] }, { coord: [next.x, next.y] }]] : prev
          }, []),
        },
      }
    })

    const xAxis = [
      {
        type: 'value',
        name: 'Recall',
        nameLocation: 'center',
        nameGap: 30,
      },
    ]
    setOption({
      tooltip,
      legend,
      grid,
      yAxis,
      xAxis,
      dataZoom: [
        {
          type: 'inside',
        },
      ],
      series,
    })
  }, [lines])

  return (
    <Card bordered={false} title={title} headStyle={{ textAlign: 'center', background: 'rgba(0, 0, 0, 0.06)' }} bodyStyle={{ padding: 0 }}>
      {lines.length ? (
        <>
          <LineChart option={option} style={{ height: '300px', width: '100%' }}></LineChart>
        </>
      ) : (
        <Empty />
      )}
    </Card>
  )
}

export default PrCurve
