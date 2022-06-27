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
  const yAxis = [
    {
      type: 'value'
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
        data: xasix,
      }
    ]
    setOption({
      tooltip,
      legend,
      // grid,
      yAxis,
      xAxis,
      series,
    })
  }, [xasix, series])

  function transferLines(lines = []) {
    let xdata = lines.map(({ line }) => line.map(([x, y, z]) => x)).flat()
    const series = lines.map(({ name, line }) => {      
      const ydata = line.map(([x, y, z]) => y)
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
    <Card bordered={false} title={title}>
      {series.length ? (
        <>
          <LineChart option={option} style={{ width: '100%' }}></LineChart>
        </>) : <Empty />}
    </Card>
  )
}

export default PrCurve
