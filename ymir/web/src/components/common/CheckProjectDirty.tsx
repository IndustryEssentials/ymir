import { Button, Row, Col, RowProps } from 'antd'
import useFetch from '@/hooks/useFetch'
import { FC, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import t from '@/utils/t'
import s from './common.less'
import { FailIcon, SuccessIcon } from './Icons'
type Props = RowProps & {
  pid: number
  initialCheck?: boolean
  callback?: (isDirty: boolean) => void
}
const CheckProjectDirty: FC<Props> = ({ pid, initialCheck, callback = () => {}, ...props }) => {
  const effect = 'project/checkStatus'
  const [{ is_dirty: isDirty }, check] = useFetch(effect, {}, true)
  const [checked, setChecked] = useState(false)
  const loading = useSelector<YStates.Root, boolean>(({ loading }) => loading.effects[effect])

  useEffect(() => {
    initialCheck && checkStatus()
  }, [])

  useEffect(() => {
    checked && callback(isDirty)
  }, [checked])

  function checkStatus() {
    check(pid)
    setChecked(true)
  }

  return (
    <Row className={s.checkPanel} gutter={20} {...props}>
      {checked ? (
        <Col flex={1} className={isDirty ? s.checkerError : s.checkerSuccess}>
          {isDirty ? (
            <>
              <FailIcon className={s.error} />
              {t('project.workspace.status.dirty', {
                dirtyLabel: <span className={s.error}>Dirty</span>,
              })}
            </>
          ) : (
            <>
              <SuccessIcon className={s.success} />{' '}
              {t('project.workspace.status.clean', {
                cleanLabel: <span className={s.success}>Clean</span>,
              })}
            </>
          )}
        </Col>
      ) : null}
      <Col>
        <Button className={s.checkBtn} onClick={checkStatus} loading={loading}>
          {t(`common.action.check${checked ? '.again' : ''}`)}
        </Button>
      </Col>
    </Row>
  )
}

export default CheckProjectDirty
