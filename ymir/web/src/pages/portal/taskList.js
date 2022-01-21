import { Card, Col, List, Row, Descriptions, Tag, } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Link, useHistory } from "umi"

import { getTaskStates, getTaskTypes } from '@/constants/query'
import t from '@/utils/t'
import EmptyState from '@/components/empty/task'
import Title from "./components/boxTitle"
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { MytaskIcon, AddtaskIcon, } from '@/components/common/icons'
import QuickAction from "./components/quickAction"
import StateTag from "@/components/task/stateTag"

const TaskList = ({ getTasks }) => {
  const history = useHistory()
  const [tasks, setTasks] = useState([])
  const types = getTaskTypes()

  useEffect(async () => {
    const result = await getTasks()
    if (result) {
      setTasks(result.items)
    }
  }, [])

  function renderType(type) {
    const target = types.find(t => t.value === type)
    return target.label
  }

  return <Card className={`${styles.box} ${styles.taskList}`} bordered={false}
    headStyle={cardHead} bodyStyle={cardBody}
    title={<Title title={<><MytaskIcon className={styles.headIcon} />{t('portal.task.my.title')}</>} link='/home/task'></Title>}
  >
    <Row gutter={10}>
      {tasks.length ? (<>
        {tasks.map(task => <Col key={task.id} span={6}>
          <Card className={styles.boxItem} hoverable title={task.name} onClick={() => { history.push(`/home/task/detail/${task.id}`) }}>
            <Descriptions column={1} colon={false}>
              <Descriptions.Item label={t('task.column.type')}>{renderType(task.type)}</Descriptions.Item>
              <Descriptions.Item label={t('task.detail.state.title')}><StateTag state={task.state} /></Descriptions.Item>
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
