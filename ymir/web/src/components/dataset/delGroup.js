import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"

const Del = forwardRef(({ delDatasetGroup, ok = () => {} }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id, name) {
    confirm({
      content: t("dataset.action.delgroup.confirm.content", { name }),
      onOk: async () => {
        const result = await delDatasetGroup(id)
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
    delDatasetGroup(id) {
      return dispatch({
        type: 'dataset/delDatasetGroup',
        payload: id,
      })
    }
  }
}

export default connect(null, actions, null, { forwardRef: true })(Del)
