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
    const labels = getLabels(versions.filter(vs => !exclude.includes(vs.id)))
    const excludeLabels = getLabels(versions.filter(vs => exclude.includes(vs.id)))
    const ids = versions.map(({ id }) => id)
    const pid = versions[0].projectId
    confirm({
      content: <div>
        <p>{t(msg, { name: labels })} </p>
        {excludeLabels.length ? <div style={{ color: 'red' }}>{t(excludeMsg, { labels: excludeLabels })}</div> : null}
      </div>,
      onOk: async () => {
        const result = await func.hide(type ? 'dataset' : 'model', pid, ids)
        console.log('result:', result)
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
