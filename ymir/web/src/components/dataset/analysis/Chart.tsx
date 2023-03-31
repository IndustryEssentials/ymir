import { FC, useEffect, useState } from 'react'
import { EChartsOption, BarSeriesOption, YAXisComponentOption, XAXisComponentOption, TooltipComponentOption } from 'echarts'
import { percent } from '@/utils/number'
import t from '@/utils/t'
import BarChart, { Props as ChartProps } from '@/components/chart/bar'
import { Chart as ChartConfig } from './AnalysisHelper'

export type Props = ChartProps & {
  customOptions: ChartConfig
}

const Chart: FC<Props> = ({ customOptions, ...resProps }) => {
  const [option, setOption] = useState<EChartsOption>({})
  const [series, setSeries] = useState<BarSeriesOption[]>([])
  const {
    xData,
    xLabel = '',
    yData,
    barWidth = 8,
    grid,
    legend,
    color,
    tooltipLabel = 'dataset.analysis.bar.asset.tooltip',
    yAxisFormatter = function (val: number) {
      return val * 100 + '%'
    },
  } = customOptions

  const defaultLegend = { itemHeight: 8, itemWidth: 20 }

  const defaultGrid = {
    left: '3%',
    right: 50,
    bottom: '3%',
    containLabel: true,
  }

  const tooltip: TooltipComponentOption = {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow',
    },
    formatter: (params) => {
      if (typeof params === 'string') {
        return params
      }
      if (!Array.isArray(params)) {
        return `${params.value}`
      }
      var res = `${params[0].name}`
      for (var i = 0, l = params.length; i < l; i++) {
        const indexColor = params[i].color
        res += `<br/><span style="display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background:${indexColor}"></span>`
        const name = params[i].seriesName
        const ratio = percent(Number(params[i].value))
        const amount = yData[params[i].seriesIndex || 0].count[params[i].dataIndex]
        res += `<span style="color: rgba(0, 0, 0, 0.85);">${name}</span>
         <span style="color: rgba(0, 0, 0, 0.45); font-size: 13px;"> ${t(tooltipLabel, { ratio, amount })}</span>`
      }
      return res
    },
  }

  const yAxis: YAXisComponentOption[] = [
    {
      type: 'value',
      splitLine: {
        lineStyle: {
          type: 'dashed',
        },
      },
      axisLabel: {
        formatter: yAxisFormatter,
      },
    },
  ]

  useEffect(() => {
    const transData = transferData()
    setSeries(transData)
  }, [customOptions])

  useEffect(() => {
    if (!series.length) {
      setOption({})
      return
    }
    const xAxis: XAXisComponentOption[] = [
      {
        type: 'category',
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        name: xLabel,
        data: xData,
        axisLabel: {
          rotate: xData.length > 10 ? 45 : 0,
        },
      },
    ]
    setOption({
      tooltip,
      legend: Object.assign(defaultLegend, legend),
      grid: Object.assign(defaultGrid, grid),
      yAxis,
      xAxis,
      color,
      series,
    })
  }, [series])

  function transferData() {
    const type: 'bar' = 'bar'
    const series = yData.map((item) => ({
      name: item.name,
      type,
      barWidth,
      data: item.value,
    }))
    return series
  }

  return <BarChart option={option} {...resProps}></BarChart>
}

export default Chart
