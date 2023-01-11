import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { message, Tag, Modal } from 'antd'
import { connect } from 'dva'

import t from '@/utils/t'
import confirmConfig from '@/components/common/DangerConfirm'
import useFetch from '@/hooks/useFetch'

import VersionName from '@/components/result/VersionName'

const Hide = forwardRef(({ type = 0, msg = 'dataset.action.hide.confirm.content', excludeMsg = 'dataset.action.hide.confirm.exclude', ok = () => {} }, ref) => {
  const [hideResult, remoteHide] = useFetch(`${!type ? 'dataset' : 'model'}/hide`)

  const [modal, contextHolder] = Modal.useModal()
  const [msgApi, msgHolder] = message.useMessage()
  const getLabels = (labels) =>
    labels.map((version) => (
      <Tag style={{ margin: '0 5px', display: 'inline-block' }} key={version.id}>
        <VersionName result={version} />
      </Tag>
    ))

  useEffect(() => hideResult && ok(hideResult), [hideResult])

  useImperativeHandle(ref, () => {
    return {
      hide,
    }
  })

  function hide(versions, exclude = []) {
    if (!versions?.length) {
      return message.warn(t('common.selected.required'))
    }
    const hideVersions = versions.filter((vs) => !exclude.includes(vs.id))
    const labels = getLabels(hideVersions)
    const excludeLabels = getLabels(versions.filter((vs) => exclude.includes(vs.id)))
    const ids = hideVersions.map(({ id }) => id)
    const pid = versions[0].projectId
    const emsg = <span style={{ display: 'inline-block', maxWidth: 800, color: 'red' }}>{t(excludeMsg, { labels: excludeLabels })}</span>
    if (!hideVersions?.length) {
      return msgApi.error(emsg)
    }
    modal.confirm(
      confirmConfig({
        content: (
          <div>
            <p>{t(msg, { name: labels })} </p>
            {excludeLabels.length ? emsg : null}
          </div>
        ),
        onOk: () => remoteHide({ pid, ids }),
        okText: t('common.action.hide'),
      }),
    )
  }

  return (
    <div>
      {contextHolder}
      {msgHolder}
    </div>
  )
})

export default connect(null, null, null, { forwardRef: true })(Hide)
