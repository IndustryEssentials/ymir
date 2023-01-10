import { CSSProperties, FC, useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts/core'
import { TooltipComponent, GridComponent, LegendComponent, MarkLineComponent, DataZoomComponent } from 'echarts/components'
import { LineChart, ScatterChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'
import { EChartsOption } from 'echarts'

type Props = {
  option: EChartsOption
  height?: number
  style?: CSSProperties
  rest?: {
    [key: string]: any
  }
}

echarts.use([TooltipComponent, GridComponent, LegendComponent, MarkLineComponent, LineChart, ScatterChart, CanvasRenderer, DataZoomComponent])

const Chart: FC<Props> = ({ option = {}, height = 300, style = {}, ...rest }) => {
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let lineChart: echarts.ECharts
    if (chartRef.current) {
      const chart = chartRef.current
      setTimeout(() => {
        lineChart = echarts.init(chart)
        lineChart.setOption(option)
      }, 50)
    }
    return () => {
      lineChart && lineChart.dispose()
    }
  }, [option])

  window.addEventListener('resize', () => {
    const chart = chartRef.current
    if (!chart) {
      return
    }
    const lineChart = echarts.getInstanceByDom(chart)
    if (lineChart && lineChart.resize) {
      const container = chart.parentElement as HTMLDivElement
      if (container) {
        var wi = getStyle(container, 'width')
        chartRef.current.style.width = wi
        lineChart.resize()
      }
    }
  })

  function getStyle(el: HTMLDivElement, name: string) {
    const style: CSSStyleDeclaration = window.getComputedStyle(el, null)
    return style.getPropertyValue(name)
  }

  return <div ref={chartRef} style={{ ...style }} {...rest}></div>
}

export default Chart
