import LineChart from "@/components/chart/line"
import { useEffect, useState } from "react"
import { Card } from "antd"

import Empty from '@/components/empty/default'


const PrCurve = ({ title='', lines }) => {
  const [option, setOption] = useState({})
  const [series, setSeries] = useState([])
  const [xasix, setXAsix] = useState([])
  const tooltip = {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  }

  const legend = { }
  const grid = {
    left: 20,
    right: 20,
    containLabel: true
  }
  const yAxis = [
    {
      type: 'value',
      name: 'Precision',
      nameLocation: 'center',
      nameGap: 30,
    }
  ]

  useEffect(() => {
    transferLines(lines)
  }, [lines])

  useEffect(() => {
    if (!series.length) {
      return
    }
    const xAxis = [
      {
        type: 'category',
        name: 'Recall',
        nameLocation: 'center',
        nameGap: 30,
        data: xasix,
      }
    ]
    setOption({
      tooltip,
      legend,
      grid,
      yAxis,
      xAxis,
      series,
    })
  }, [xasix, series])

  function getP(line, field = 'x') {
    return line ? line.map(point => point[field]) : null
  }

  function transferLines(lines = []) {
    let xdata = lines.map(({ line }) => getP(line)).flat()
    const series = lines.map(({ name, line }) => {      
      const ydata = getP(line, 'y')
      return {
        name,
        type: 'line',
        smooth: true,
        showSymbol: false,
        label: { show: true, formatter: '{@[0]}' },
        emphasis: {
          focus: 'series'
        },
        data: ydata,
      }
    })

    setXAsix([...new Set(xdata)])
    setSeries(series)
  }

  return (
    <Card bordered={false} title={title} headStyle={{ textAlign: 'center', background: 'rgba(0, 0, 0, 0.06)' }} bodyStyle={{ padding: 0 }}>
      {series.length ? (
        <>
          <LineChart option={option} style={{ height: '300px', width: '100%' }}></LineChart>
        </>) : <Empty />}
    </Card>
  )
}

export default PrCurve
