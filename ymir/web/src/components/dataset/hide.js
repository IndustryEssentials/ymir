import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"

const Hide = forwardRef(({ ok = () => {}, ...func }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      hide,
    }
  })

  function hide(versions) {
    const labels = versions.map(version => <span style={{ margin: '0 5px', display: 'inline-block' }} key={version.id}>{version.name} {version.versionName}</span>)
    const ids = versions.map(({ id }) => id)
    confirm({
      content: t("dataset.action.hide.confirm.content", { name: labels }),
      onOk: async () => {
        const result = await func.hideDataset(ids)
        if (result) {
          // todo return result to parent handle
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
    hideDataset(id) {
      return dispatch({
        type: 'dataset/hideDatasets',
        payload: id,
      })
    }
  }
}

export default connect(null, actions, null, { forwardRef: true })(Hide)
