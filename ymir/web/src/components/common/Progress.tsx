import { Col, Progress, Row } from 'antd'
import { getLocale, Link } from 'umi'

import { ResultStates } from '@/constants/common'
import t from '@/utils/t'
import StateTag from '../task/StateTag'
import { calTimeLeft } from '@/utils/date'

function RenderProgress(state: ResultStates, result: YModels.AllResult, simple = false) {
  const { id, progress, createTime, taskState, task } = result
  if (ResultStates.READY === state && task?.is_terminated) {
    return t('task.state.terminating')
  }
  if (!taskState) {
    return
  }
  const fixedProgress = ResultStates.VALID !== state && progress === 1 ? 0.99 : progress
  const percent = Math.floor(fixedProgress * 100)
  const stateTag = <StateTag mode={simple ? 'icon' : 'text'} state={state} code={task.error_code} />
  return state === ResultStates.READY ? (
    <Row gutter={10} style={{ alignItems: 'center', padding: '0 7px', textAlign: 'left' }}>
      <Col>{stateTag}</Col>
      <Col flex={1}>
        <Progress size="small" percent={percent} strokeWidth={8} strokeColor={'rgb(250, 211, 55)'} trailColor={'rgba(0, 0, 0, 0.06)'} />
        <div style={{ color: 'rgba(0, 0, 0, 0.45)' }}>
          {t('task.column.state.timeleft.label')}
          {calTimeLeft(percent, createTime, getLocale())}
        </div>
      </Col>
    </Row>
  ) : (
    stateTag
  )
}

export default RenderProgress
