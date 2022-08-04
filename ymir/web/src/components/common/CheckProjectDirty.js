import { Button, Row, Col, Space, Tag } from "antd"
import useProjectStatus from "@/hooks/useProjectStatus"
import { useEffect, useState } from "react"

import t from '@/utils/t'
import s from './common.less'
import { FailIcon, SuccessIcon } from "./icons"

const CheckProjectDirty = ({ pid, initialCheck, callback = () => { }, ...props }) => {
  const { checkDirty } = useProjectStatus(pid)
  const [isDirty, setDirty] = useState(null)
  const [checked, setChecked] = useState(false)
  useEffect(() => {
    initialCheck && checkStatus()
  }, [])

  async function checkStatus() {
    const dirty = await checkDirty()
    setDirty(dirty)
    setChecked(true)
    callback(dirty)
  }

  return <Row className={s.checkPanel} gutter={20} {...props}>
    {checked ?
      <Col flex={1} className={isDirty ? s.checkerError : s.checkerSuccess}>
        {isDirty ?
          <><FailIcon className={s.error} />{t('project.workspace.status.dirty', {
            dirtyLabel: <span className={s.error}>Dirty</span>
          })}</> :
          <><SuccessIcon className={s.success} /> {t('project.workspace.status.clean', {
            cleanLabel: <span className={s.success}>Clean</span>
          })}</>
        }
      </Col>
      : null}
    <Col>
      <Button className={s.checkBtn} onClick={checkStatus}>{t(`common.action.check${checked ? '.again' : ''}`)}</Button>
    </Col>
  </Row>
}

export default CheckProjectDirty
