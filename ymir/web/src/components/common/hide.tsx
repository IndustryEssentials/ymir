import { forwardRef, useEffect, useImperativeHandle } from 'react'
import { message, Tag, Modal } from 'antd'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'

import confirmConfig from '@/components/common/DangerConfirm'
import VersionName from '@/components/result/VersionName'
type ResultType = 'dataset' | 'model' | 'prediction'
type Target = {
  id: number
  projectId: number
  groupId: number
  name: string
}
export type RefProps = {
  hide: (dss: Target[], exclude?: number[]) => void
}
type Props = {
  type?: ResultType
  msg?: string
  excludeMsg?: string
  ok?: (result: Target[]) => void
}

const Hide = forwardRef<RefProps, Props>(
  ({ type = 'dataset', msg = 'dataset.action.del.confirm.content', excludeMsg = 'dataset.action.del.confirm.exclude', ok = () => {} }, ref) => {
    const { data: hideResult, run: remoteHide } = useRequest<Target[], [{ pid: number; ids: number[] }]>(`${type}/hide`)

    const [modal, contextHolder] = Modal.useModal()
    const [msgApi, msgHolder] = message.useMessage()
    const getLabels = (labels: Target[]) =>
      labels.map((version) => (
        <Tag style={{ margin: '0 5px', display: 'inline-block' }} key={version.id}>
          <VersionName result={version} />
        </Tag>
      ))

    useEffect(() => hideResult && ok(hideResult), [hideResult])

    useImperativeHandle(
      ref,
      () => ({
        hide,
      }),
      [],
    )

    function hide(versions: Target[], exclude: number[] = []) {
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
