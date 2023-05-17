import { Button, Row, Col, RowProps } from 'antd'
import { FC, useEffect, useState } from 'react'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import s from './common.less'
import { FailIcon, SuccessIcon } from './Icons'
type Props = RowProps & {
  pid: number
  initialCheck?: boolean
  callback?: (isDirty: boolean) => void
}
const CheckProjectDirty: FC<Props> = ({ pid, initialCheck, callback = () => {}, ...props }) => {
  const effect = 'project/checkStatus'
  const { data: { is_dirty: isDirty } = { is_dirty: false }, run: check, loading } = useRequest<{ is_dirty?: boolean }, [number]>(effect, { loading: false })
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    initialCheck && checkStatus()
  }, [])

  useEffect(() => {
    checked && callback(!!isDirty)
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
