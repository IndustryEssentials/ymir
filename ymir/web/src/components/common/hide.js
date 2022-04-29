import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"
import { message } from "antd"

const Hide = forwardRef(({ type = 0, msg = 'dataset.action.hide.confirm.content', ok = () => { }, ...func }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      hide,
    }
  })

  function hide(versions) {
    if (!versions?.length) {
      return message.warn(t('common.selected.required'))
    }
    const labels = versions.map(version => <span
      style={{ margin: '0 5px', display: 'inline-block' }}
      key={version.id}>
      {version.name} {version.versionName}
    </span>)
    const ids = versions.map(({ id }) => id)
    const pid = versions[0].projectId
    confirm({
      content: t(msg, { name: labels }),
      onOk: async () => {
        const result = await func[type ? 'hideModels' : 'hideDatasets'](pid, ids)
        if (result) {
          ok(result)
        }
      },
      okText: t('common.action.hide'),
    })
  }

  return null
})

const actions = (dispatch) => {
  return {
    hideDatasets(pid, ids) {
      return dispatch({
        type: `dataset/hideDatasets`,
        payload: {pid, ids},
      })
    },
    hideModels(pid, ids) {
      return dispatch({
        type: `model/hideModels`,
        payload: {pid, ids},
      })
    },
  }
}

export default connect(null, actions, null, { forwardRef: true })(Hide)
