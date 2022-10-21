import { forwardRef, useEffect, useImperativeHandle } from "react"

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'

import confirm from '@/components/common/dangerConfirm'

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
    confirm({
      content: t("image.del.confirm.content", { name }),
      onOk: () => delImage(id),
      okText: t('common.del'),
    })
  }

  return null
})

export default Del