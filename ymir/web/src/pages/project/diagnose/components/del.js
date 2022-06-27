import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"

const Del = forwardRef(({ delVisualization, ok = () => {} }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id) {
    confirm({
      content: t('visualization.del.confirm.content'),
      onOk: async () => {
        const result = await delVisualization(id)
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
    delVisualization(id) {
      return dispatch({
        type: 'visualization/delVisualization',
        payload: id,
      })
    }
  }
}

export default connect(null, actions, null, { forwardRef: true })(Del)