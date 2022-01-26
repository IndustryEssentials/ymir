import { Col, Progress, Row } from "antd"
import { getLocale, Link } from "umi"

import { TASKSTATES } from "@/constants/task"
import t from "@/utils/t"
import StateTag from "../task/stateTag"
import { calTimeLeft } from "@/utils/date"
import { InprogressIcon } from "./icons"

function RenderProgress(state, { id, progress, create_datetime }, simple=false) {
  if (!state) {
    return
  }
  const stateTag = <StateTag mode={simple ? 'icon' : 'text'} state={state} />
  if (state === TASKSTATES.DOING) {
    return (
      <Row gutter={10} style={{ alignItems: 'center', padding: '0 7px', textAlign: 'left' }}>
        <Col>
          <InprogressIcon style={{ fontSize: 18, color: 'rgb(250, 211, 55)'}} />
        </Col>
        <Col flex={1}>
          <Progress size="small" percent={progress} strokeWidth={8} strokeColor={'rgb(250, 211, 55)'} trailColor={'rgba(0, 0, 0, 0.06)'} />
          <div style={{color: 'rgba(0, 0, 0, 0.45)'}}>
            {t('task.column.state.timeleft.label')}{calTimeLeft(progress, create_datetime, getLocale())}</div>
        </Col>
      </Row>
    )
  } else if (!simple && [TASKSTATES.FAILURE, TASKSTATES.FINISH].indexOf(state) > -1) {
    return <Link to={`/home/task/detail/${id}#result`}>{stateTag}</Link>
  } else {
    return stateTag
  }
}

export default RenderProgress
