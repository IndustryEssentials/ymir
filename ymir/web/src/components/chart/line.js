import { useEffect, useRef, useState } from "react"
import * as echarts from 'echarts/core';
import {
    TooltipComponent,
    GridComponent,
    LegendComponent,
    MarkLineComponent
} from 'echarts/components'
import {
    LineChart,
} from 'echarts/charts'
import {
    CanvasRenderer
} from 'echarts/renderers'

echarts.use(
    [TooltipComponent, GridComponent, LegendComponent, MarkLineComponent, LineChart, CanvasRenderer]
);

const Chart = ({ option = {}, height = 300, style = {}, ...rest }) => {
  const chartRef = useRef(null)
  
  useEffect(() => {
    let lineChart = null
    // console.log('option: ', option, chartRef)
    if (chartRef.current) {
      const chart = chartRef.current
      lineChart = echarts.init(chart)
      lineChart.setOption(option)
    }
    return () => {
      lineChart && lineChart.dispose()
    }
  }, [option])

  window.addEventListener('resize', () => {
    if (!chartRef.current) {
      return
    }
    const lineChart = echarts.getInstanceByDom(chartRef.current)
    if (lineChart && lineChart.resize) {
      lineChart.resize()
    }
  })

  return <div ref={chartRef} style={{height,  ...style, }} {...rest}>&nbsp;</div>
}

export default Chart
