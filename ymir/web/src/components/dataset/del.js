import t from '@/utils/t'
import confirmConfig from '@/components/common/DangerConfirm'
import { connect } from 'dva'
import { forwardRef, useImperativeHandle } from 'react'
import { Modal } from 'antd'

const Del = forwardRef(({ delDataset, ok = () => {} }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      del,
    }
  })

  function del(id, name) {
    Modal.confirm(
      confirmConfig({
        content: t('dataset.action.del.confirm.content', { name }),
        onOk: async () => {
          const result = await delDataset(id)
          if (result) {
            ok(result.dataset_group_id)
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
    delDataset(id) {
      return dispatch({
        type: 'dataset/delDataset',
        payload: id,
      })
    },
  }
}

export default connect(null, actions, null, { forwardRef: true })(Del)
