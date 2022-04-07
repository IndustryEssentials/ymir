import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"

const Del = forwardRef(({ delModel, ok = () => {} }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id, name) {
    confirm({
      content: t("model.action.del.confirm.content", { name }),
      onOk: async () => {
        const result = await delModel(id)
        if (result) {
          ok(result.model_group_id)
        }
      },
      okText: t('common.del'),
    })
  }

  return null
})

const actions = (dispatch) => {
  return {
    delModel(id) {
      return dispatch({
        type: 'model/delModel',
        payload: id,
      })
    }
  }
}

export default connect(null, actions, null, { forwardRef: true })(Del)
