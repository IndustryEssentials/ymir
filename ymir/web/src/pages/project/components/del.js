import t from '@/utils/t'
import confirmConfig from '@/components/common/DangerConfirm'
import { connect } from 'dva'
import { forwardRef, useImperativeHandle } from 'react'
import { Modal } from 'antd'

const Del = forwardRef(({ delProject, ok = () => {} }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id, name) {
    Modal.confirm(
      confirmConfig({
        content: t('project.del.confirm.content', { name }),
        onOk: async () => {
          const result = await delProject(id)
          if (result) {
            ok(id)
          }
        },
        okText: t('common.del'),
      }),
    )
  }

  return null
})

const actions = (dispatch) => {
  return {
    delProject(id) {
      return dispatch({
        type: 'project/delProject',
        payload: id,
      })
    },
  }
}

export default connect(null, actions, null, { forwardRef: true })(Del)
