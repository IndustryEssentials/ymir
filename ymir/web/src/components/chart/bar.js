import { useEffect, useRef, useState } from "react"
import * as echarts from 'echarts/core';
import {
    TooltipComponent,
    GridComponent,
    LegendComponent,
    MarkLineComponent
} from 'echarts/components'
import {
    BarChart, LineChart,
} from 'echarts/charts'
import {
    CanvasRenderer
} from 'echarts/renderers'

echarts.use(
    [TooltipComponent, GridComponent, LegendComponent, MarkLineComponent, BarChart, LineChart, CanvasRenderer]
);

const Chart = ({ option = {}, height = 300 }) => {
  const chartRef = useRef(null)
  
  useEffect(() => {
    let barChart = null
    // console.log('option: ', option, chartRef)
    if (chartRef.current) {
      const chart = chartRef.current
      barChart = echarts.init(chart)
      barChart.setOption(option)
    }
    return () => {
      barChart && barChart.dispose()
    }
  }, [option])

  window.addEventListener('resize', () => {
    if (!chartRef.current) {
      return
    }
    const barChart = echarts.getInstanceByDom(chartRef.current)
    if (barChart && barChart.resize) {
      barChart.resize()
    }
  })

  return <div ref={chartRef} style={{height}}>&nbsp;</div>
}

export default Chart
