import { Col, Progress, Row } from "antd"
import { getLocale, Link } from "umi"

import { states } from "@/constants/dataset"
import t from "@/utils/t"
import StateTag from "../task/stateTag"
import { calTimeLeft } from "@/utils/date"
import { InprogressIcon } from "./icons"

function RenderProgress(state, { id, progress, createTime, taskState, task = {} }, simple = false) {
  if (states.READY === state && task?.is_terminated) {
    return t('task.state.terminating')
  }
  if (!taskState) {
    return
  }
  const percent = Math.floor(progress * 100)
  const stateTag = <StateTag mode={simple ? 'icon' : 'text'} state={state} />
  return state === states.READY ? (
    <Row gutter={10} style={{ alignItems: 'center', padding: '0 7px', textAlign: 'left' }}>
      <Col>
        {stateTag}
      </Col>
      <Col flex={1}>
        <Progress size="small" percent={percent} strokeWidth={8} strokeColor={'rgb(250, 211, 55)'} trailColor={'rgba(0, 0, 0, 0.06)'} />
        <div style={{ color: 'rgba(0, 0, 0, 0.45)' }}>
          {t('task.column.state.timeleft.label')}{calTimeLeft(percent, createTime, getLocale())}</div>
      </Col>
    </Row>
  ) : stateTag
}

export default RenderProgress
