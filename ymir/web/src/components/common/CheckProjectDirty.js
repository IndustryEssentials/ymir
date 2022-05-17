import { Button, Space, Tag } from "antd"
import useProjectStatus from "@/hooks/useProjectStatus"
import { useEffect, useState } from "react"

import t from '@/utils/t'

const CheckProjectDirty = ({ pid, initialCheck, callback = () => {}, ...props }) => {
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

  return <Space {...props}>
    {checked ?
      isDirty ? t('project.workspace.status.dirty', { dirtyLabel: <Tag color={'error'}>Dirty</Tag> })
        : t('project.workspace.status.clean', { cleanLabel: <Tag color={'success'}>Clean</Tag> })
      : null}
    <Button type='primary' size="small" onClick={checkStatus}>{t(`common.action.check${checked ? '.again' : ''}`)}</Button>
  </Space>
}

export default CheckProjectDirty
