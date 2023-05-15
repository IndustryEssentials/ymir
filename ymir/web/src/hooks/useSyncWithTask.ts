import { Dataset, Image, Model, Prediction } from '@/constants'
import { useEffect, useState } from 'react'
import { useSelector } from 'umi'
type AllResult = Prediction | Dataset | Model
type Result = AllResult | AllResult[]
const useSyncState = <DataType extends Result>(fresh: Function) => {
  const [data, setData] = useState<DataType>()

  const tasks = useSelector(({ socket }) => socket.tasks)

  useEffect(() => {
    if (!tasks || !data) {
      return
    }
    if (Array.isArray(data)) {
      const updateList = data.map(getUpdateData)
      // setData(updateList)
    } else {
    }
  }, [tasks])
  const getUpdateData = (dt: AllResult) => {
    const task = tasks.find((task) => task.hash === dt.hash)
    return task
      ? {
          ...dt,
          state: task.result_state,
          progress: task.percent,
          taskState: task.state,
          task: { ...dt.task, state: task.state, percent: task.percent },
        }
      : dt
  }

  return [data, setData]
}

export default useSyncState
