import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { Modal } from 'antd'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'

import confirmConfig from '@/components/common/DangerConfirm'
import { Image } from '@/constants'

type DelFunc = (id: number, name: string) => void
export type RefProps = {
  del: DelFunc
}

export type Props = {
  ok?: (id: number) => void
}

const Del = forwardRef<RefProps, Props>(({ ok = () => {} }, ref) => {
  const { data: delResult, run: delImage } = useRequest<Image, [number]>('image/delImage')

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

  const del: DelFunc = (id, name) => {
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
