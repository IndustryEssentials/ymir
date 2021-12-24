import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"

const Del = forwardRef(({ delImage, ok = () => {} }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id, name) {
    confirm({
      content: t("image.del.confirm.content", { name }),
      onOk: async () => {
        const result = await delImage(id)
        if (result) {
          ok(id)
        }
      },
      okText: t('common.del'),
    })
  }

  return null
})

const actions = (dispatch) => {
  return {
    delImage(id) {
      return dispatch({
        type: 'image/delImage',
        payload: id,
      })
    }
  }
}

export default connect(null, actions, null, { forwardRef: true })(Del)