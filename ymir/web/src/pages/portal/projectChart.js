import BarChart from "@/components/chart/bar"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Card, Radio } from "antd"
import moment from "moment"

import t from '@/utils/t'
import styles from './index.less'
import Empty from '@/components/empty/default'
import { cardBody, cardHead } from "./components/styles"
import { BarchartIcon } from '@/components/common/icons'

const getTimes = () => [
  { value: 'day', label: 'Day', },
  { value: 'week', label: 'Week', },
  { value: 'month', label: 'Month', },
]

const ProjectChart = ({ getProjectStats }) => {
  const times = getTimes()
  const [option, setOption] = useState({})
  const [series, setSeries] = useState([])
  const [type, setType] = useState(times[0].value)
  const tooltip = {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  }

  const legend = { data: [t('portal.project')], left: 0 }
  const grid = {
    left: '0',
    right: '5px',
    bottom: '3%',
    containLabel: true
  }
  const yAxis = [
    {
      type: 'value'
    }
  ]
  const [timestamps, setTimestamps] = useState([])

  useEffect(async () => {
    const result = await getProjectStats(type)
    if (result && result.records) {
      const transData = transferData(result.records)
      setTimestamps(result.timestamps)
      setSeries(transData)
    }
  }, [type])

  useEffect(() => {
    if(!series.length) {
      return
    }
    const xAxis = [
      {
        type: 'category',
        data: xTimes(type),
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
  }, [series])

  function transferData(data) {
    let result = [];
    data.forEach(item => {
      // filter
      result.push(item[1])
    })
     const series = [{
      name: t('portal.project'),
      type: 'line',
      smooth: true,
      label: { show: true, formatter: '{@[0]}' },
      emphasis: {
        focus: 'series'
      },
      data: result,
    }]
    return series
  }

  // labels
  function xTimes(type) {
    let result = []
    const e8 = (stamp) => (stamp ? moment(stamp) : moment()).utcOffset(480)
    // day
    if (type === times[0].value) {
      result = timestamps.map(stamp => {
        return e8(stamp).format('DD/MM')
      })
    } else if (type === times[1].value) {
      // week
      return timestamps.map(stamp => {
        return e8(stamp).format('D/M')
      })
    } else {
      // year
      result = timestamps.map(stamp => {
        return e8(stamp).format('MM/YY')
      })
    }
    return result
  }

  function timeChange ({ target }){ 
    setType(target.value) 
  }

  return (
    <Card className={styles.box}
      headStyle={cardHead} bodyStyle={{...cardBody, height: 281}} 
      bordered={false} title={<><BarchartIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.project.static.title')}</span></>}
    >
      {series.length ? (
      <>
        {console.log('option: ',option)}
        <Radio.Group className={styles.taskTimeBtn} options={times} optionType='button' value={type} onChange={timeChange}></Radio.Group>
        <BarChart option={option} height={241}></BarChart>
      </>) : <Empty /> }
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getProjectStats(type) {
      return dispatch({
        type: 'common/getStats',
        payload: { q: 'ps', type, }
      })
    }
  }
}

export default connect(null, actions)(ProjectChart)
