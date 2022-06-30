import { Button, Row, Col, Space, Tag } from "antd"
import useProjectStatus from "@/hooks/useProjectStatus"
import { useEffect, useState } from "react"

import t from '@/utils/t'
import s from './common.less'

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

  return <Row gutter={20} {...props}>
    {checked ?
      <Col flex={1} className={isDirty ? s.checkerError : s.checkerSuccess}>
        {isDirty ? t('project.workspace.status.dirty', {dirtyLabel: <span style={{ color: 'red' }}>Dirty</span> })
        : t('project.workspace.status.clean', {cleanLabel: <span style={{ color: 'green' }}>Clean</span> })}
      </Col>
      : null}
    <Col>
      <Button type='primary' onClick={checkStatus}>{t(`common.action.check${checked ? '.again' : ''}`)}</Button>
    </Col>
  </Row>
}

export default CheckProjectDirty
