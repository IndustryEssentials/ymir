import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { Modal } from 'antd'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'

import confirmConfig from '@/components/common/DangerConfirm'

const Del = forwardRef(({ ok = () => {} }, ref) => {
  const [delResult, delImage] = useFetch('image/delImage')

  useEffect(() => {
    if (delResult) {
      ok(delResult.id)
    }
  }, [delResult])

  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id, name) {
    Modal.confirm(
      confirmConfig({
        content: t('image.del.confirm.content', { name }),
        onOk: () => delImage(id),
        okText: t('common.del'),
      }),
    )
  }

  return null
})

export default Del
