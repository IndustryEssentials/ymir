import { Card, Col, List, Row, Descriptions, Tag, } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Link, useHistory } from "umi"

import { getTaskStates, getTaskTypes } from '@/constants/query'
import { TASKTYPES, TASKSTATES } from '@/constants/task'
import t from '@/utils/t'
import EmptyState from '@/components/empty/task'
import renderTitle from "./components/boxTitle"
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { MytaskIcon, AddtaskIcon, InprogressIcon, SuccessIcon, FailIcon, } from '@/components/common/icons'
import QuickAction from "./components/quickAction"

const TaskList = ({ getTasks }) => {
  const history = useHistory()
  const [tasks, setTasks] = useState([])
  const states = getTaskStates()
  const types = getTaskTypes()

  useEffect(async () => {
    // setTasks([
    //   {
    //     id: 100343,
    //     name: 'task name1',
    //     type: 1,
    //     state: 2,
    //   },
    //   {
    //     id: 100343,
    //     name: 'task name1',
    //     type: 2,
    //     state: 3,
    //   },
    //   {
    //     id: 100343,
    //     name: 'task name1',
    //     type: 3,
    //     state: 4,
    //   },
    // ])
    const result = await getTasks()
    if (result) {
      setTasks(result.items)
    }
  }, [])

  const stateLabel = (state) => {
    const result = states.find(s => s.value === state)
    return result.label
  }

  function renderType(type) {
    const target = types.find(t => t.value === type)
    return target.label
  }

  function renderState(state) {
    state = state || TASKSTATES.PENDING
    const iconStyle = { fontSize: 14, position: 'relative', marginRight: 3 }
    const maps = {
      [TASKSTATES.PENDING]: { icon: <InprogressIcon style={iconStyle} />, color: 'gray' },
      [TASKSTATES.DOING]: { icon: <InprogressIcon style={iconStyle} />, color: 'warning' },
      [TASKSTATES.FINISH]: { icon: <SuccessIcon style={iconStyle} />, color: 'success' },
      [TASKSTATES.FAILURE]: { icon: <FailIcon style={iconStyle} />, color: 'error' },
    }
    const target = states.find(s => s.value === state)
    return <Tag color={maps[target.value].color}>{maps[target.value].icon}{target.label}</Tag>
  }

  return <Card className={`${styles.box} ${styles.hotModel}`} bordered={false}
    headStyle={cardHead} bodyStyle={cardBody}
    title={renderTitle(<><MytaskIcon className={styles.headIcon} />{t('portal.task.my.title')}</>, '/home/task')}
  >
    <Row gutter={10}>
      {tasks.length ? (<>
        {tasks.map(task => <Col key={task.id} span={6}>
          <Card className={styles.boxItem} hoverable title={task.name} onClick={() => { history.push(`/home/task/detail/${task.id}`) }}>
            <Descriptions column={1} colon={false}>
              <Descriptions.Item label={t('task.column.type')}>{renderType(task.type)}</Descriptions.Item>
              <Descriptions.Item label={t('task.detail.state.title')}>{renderState(task.state)}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>)}
        <QuickAction icon={<AddtaskIcon style={{ fontSize: 50, color: '#36cbcb' }} />} label={t('portal.action.new.task')} link={'/home/task'}></QuickAction>
      </>) :
        <EmptyState style={{ height: 236 }} />
      }
    </Row>
  </Card>
}

const actions = (dispatch) => {
  return {
    getTasks() {
      return dispatch({
        type: 'task/getTasks',
        payload: { offset: 0, limit: 3 },
      })
    }
  }
}

export default connect(null, actions)(TaskList)
