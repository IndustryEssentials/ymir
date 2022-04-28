import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"

const Hide = forwardRef(({ type = 0, msg = 'dataset.action.hide.confirm.content', ok = () => { }, ...func }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      hide,
    }
  })

  function hide(versions) {
    const labels = versions.map(version => <span
      style={{ margin: '0 5px', display: 'inline-block' }}
      key={version.id}>
      {version.name} {version.versionName}
    </span>)
    const ids = versions.map(({ id }) => id)
    confirm({
      content: t(msg, { name: labels }),
      onOk: async () => {
        const result = await func[type ? 'hideModels' : 'hideDatasets'](ids)
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
    hideDatasets(ids) {
      return dispatch({
        type: `dataset/hideDatasets`,
        payload: ids,
      })
    },
    hideModels(ids) {
      return dispatch({
        type: `model/hideModels`,
        payload: ids,
      })
    },
  }
}

export default connect(null, actions, null, { forwardRef: true })(Hide)
