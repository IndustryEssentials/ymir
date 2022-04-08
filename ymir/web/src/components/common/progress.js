import { Col, Progress, Row } from "antd"
import { getLocale, Link } from "umi"

import { states } from "@/constants/dataset"
import t from "@/utils/t"
import StateTag from "../task/stateTag"
import { calTimeLeft } from "@/utils/date"
import { InprogressIcon } from "./icons"

function RenderProgress(state, { id, progress, createTime, taskState }, simple = false) {
  if (!taskState) {
    return
  }
  const stateTag = <StateTag mode={simple ? 'icon' : 'text'} state={state} />
  return state === states.READY ? (
    <Row gutter={10} style={{ alignItems: 'center', padding: '0 7px', textAlign: 'left' }}>
      <Col>
        <InprogressIcon style={{ fontSize: 18, color: 'rgb(250, 211, 55)' }} />
      </Col>
      <Col flex={1}>
        <Progress size="small" percent={Math.floor(progress * 100)} strokeWidth={8} strokeColor={'rgb(250, 211, 55)'} trailColor={'rgba(0, 0, 0, 0.06)'} />
        <div style={{ color: 'rgba(0, 0, 0, 0.45)' }}>
          {t('task.column.state.timeleft.label')}{calTimeLeft(progress, createTime, getLocale())}</div>
      </Col>
    </Row>
  ) : stateTag
}

export default RenderProgress
