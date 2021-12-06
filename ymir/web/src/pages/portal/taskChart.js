import BarChart from "@/components/chart/bar"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Card, Radio } from "antd"
import moment from "moment"

import { getTaskTypes } from '@/constants/query'
import { TASKTYPES } from '@/constants/task'
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

const TaskChart = ({ getTaskStats }) => {
  const times = getTimes()
  const [option, setOption] = useState({})
  const [series, setSeries] = useState([])
  const [type, setType] = useState(times[0].value)
  const types = getTaskTypes()
  types.shift()
  const tooltip = {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  }
  const legend = { data: types.map(type => type.label), left: 0 }
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
    const result = await getTaskStats(type)
    // console.log('get task stats: ', result)
    if (result && result.task) {
      const transData = transferData(result.task)
      // console.log('transfered: ', transData)
      setTimestamps(result.task_timestamps)
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
    const result = {}
    types.forEach(type => result[type.value] = [])
    data.forEach(item => {
      // filter
      result[TASKTYPES.FILTER].push(item[TASKTYPES.FILTER])
      result[TASKTYPES.TRAINING].push(item[TASKTYPES.TRAINING])
      result[TASKTYPES.MINING].push(item[TASKTYPES.MINING])
      result[TASKTYPES.LABEL].push(item[TASKTYPES.LABEL])
    })
    const series = types.map(type => ({
      name: type.label,
      type: 'line',
      smooth: true,
      label: { show: true, formatter: '{@[0]}' },
      emphasis: {
        focus: 'series'
      },
      data: result[type.value].reverse(),
    }))
    return series
  }

  // labels
  function xTimes(type) {
    let result = []
    const e8 = (stamp) => (stamp ? moment(Number(stamp) * 1000) : moment()).utcOffset(480)
    // day
    if (type === times[0].value) {
      result = timestamps.map(stamp => {
        return e8(stamp).format('DD/MM')
      })
    } else if (type === times[1].value) {
      // week
      return timestamps.map(stamp => {
        return e8(stamp).format('D/M')
      }).reverse()
    } else {
      // year
      result = timestamps.map(stamp => {
        return e8(stamp).format('MM/YY')
      })
    }
    // console.log('xaxis data: ', result)
    // return timestamps.reverse()
    return result.reverse()
  }

  function timeChange ({ target }){ 
    setType(target.value) 
  }

  return (
    <Card className={styles.box}
      headStyle={cardHead} bodyStyle={{...cardBody, height: 281}} 
      bordered={false} title={<><BarchartIcon className={styles.headIcon} />{t('portal.task.static.title')}</>}
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
    getTaskStats(type) {
      return dispatch({
        type: 'common/getStats',
        payload: { q: 'task', type, }
      })
    }
  }
}

export default connect(null, actions)(TaskChart)
