import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { message, Tag, Modal } from 'antd'

import t from '@/utils/t'
import confirmConfig from '@/components/common/DangerConfirm'
import useFetch from '@/hooks/useFetch'

import VersionName from '@/components/result/VersionName'

export type RefProps = {
  hide: (dss: YModels.Result[], exclude?: number[]) => void
}
type Props = {
  type?: 'dataset' | 'model' | 'prediction'
  msg?: string
  excludeMsg?: string
  ok?: (result: YModels.Result) => void
}

const Hide = forwardRef<RefProps, Props>(
  ({ type = 'dataset', msg = 'dataset.action.del.confirm.content', excludeMsg = 'dataset.action.del.confirm.exclude', ok = () => {} }, ref) => {
    const [hideResult, remoteHide] = useFetch(`${type}/hide`)

    const [modal, contextHolder] = Modal.useModal()
    const [msgApi, msgHolder] = message.useMessage()
    const getLabels = (labels: YModels.Result[]) =>
      labels.map((version) => (
        <Tag style={{ margin: '0 5px', display: 'inline-block' }} key={version.id}>
          <VersionName result={version} />
        </Tag>
      ))

    useEffect(() => hideResult && ok(hideResult), [hideResult])

    useImperativeHandle(ref, () => ({
        hide,
    }), [])

    function hide(versions: YModels.Result[], exclude: number[] = []) {
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
          okText: t('common.action.del'),
        }),
      )
    }

    return (
      <div>
        {contextHolder}
        {msgHolder}
      </div>
    )
  },
)

export default Hide
