import t from "@/utils/t"
import confirm from '@/components/common/dangerConfirm'
import { connect } from "dva"
import { forwardRef, useImperativeHandle } from "react"
import { message, Tag } from "antd"

const Hide = forwardRef(({ type = 0, msg = 'dataset.action.hide.confirm.content',
  excludeMsg = 'dataset.action.hide.confirm.exclude', ok = () => { }, ...func }, ref) => {
  useImperativeHandle(ref, () => {
    return {
      hide,
    }
  })

  function hide(versions, exclude = []) {
    if (!versions?.length) {
      return message.warn(t('common.selected.required'))
    }
    const hideVersions = versions.filter(vs => !exclude.includes(vs.id))
    const labels = getLabels(hideVersions)
    const excludeLabels = getLabels(versions.filter(vs => exclude.includes(vs.id)))
    const ids = hideVersions.map(({ id }) => id)
    const pid = versions[0].projectId
    const emsg = <div style={{ color: 'red' }}>{t(excludeMsg, { labels: excludeLabels })}</div>
    if (!hideVersions?.length) {
      return message.error(emsg)
    }
    confirm({
      content: <div>
        <p>{t(msg, { name: labels })} </p>
        {excludeLabels.length ? emsg : null}
      </div>,
      onOk: async () => {
        const result = await func.hide(!type ? 'dataset' : 'model', pid, ids)
        if (result) {
          ok(result)
        }
      },
      okText: t('common.action.hide'),
    })
  }

  return null
})

const getLabels = (labels) => labels.map(version => <Tag
  style={{ margin: '0 5px', display: 'inline-block' }}
  key={version.id}>
  {version.name} {version.versionName}
</Tag>)

const actions = (dispatch) => {
  return {
    hide(module = 'dataset', pid, ids) {
      const type = `${module}/hide`
      return dispatch({
        type,
        payload: { pid, ids, },
      })
    },
  }
}

export default connect(null, actions, null, { forwardRef: true })(Hide)
