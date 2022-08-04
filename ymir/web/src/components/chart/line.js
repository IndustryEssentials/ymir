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
      setTimeout(() => {
        lineChart = echarts.init(chartRef.current)
        lineChart.setOption(option)
      }, 50)
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
      const container = chartRef.current.parentElement
      var wi = getStyle(container, 'width')
      chartRef.current.style.width = wi
      lineChart.resize()
    }
  })

  function getStyle(el, name) {
    if (window.getComputedStyle) {
      return window.getComputedStyle(el, null)[name]
    } else {
      return el.currentStyle[name]
    }
  }


  return <div ref={chartRef} style={{ ...style, }} {...rest}>&nbsp;</div>
}

export default Chart
