import { Alert, Button, Card, Form, message, Modal, Space } from 'antd'
import { FC, useCallback, useEffect } from 'react'
import t from '@/utils/t'
import AddList from './add/AddList'
import AddSelector from './add/AddSelector'
import FormatDetailModal from '@/components/dataset/FormatDetailModal'

import s from './add.less'
import { Prompt, useHistory, useParams, useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import { Task } from '@/constants'

const BatchAdd: FC = () => {
  const { id } = useParams<{ id: string }>()
  const history = useHistory()
  const { formatVisible: visible, items, editing } = useSelector(({ dataset }) => dataset.importing)
  const { run: showFormatDetail } = useRequest<null, [boolean]>('dataset/showFormatDetail', { loading: false })
  const { data: results, run: batch } = useRequest<(Task | null)[], [{ pid: string }]>('dataset/batchAdd')

  useEffect(() => {
    results && history.push(`/home/project/${id}/dataset`)
    if (results?.length) {
      const validResults = results.filter((tru) => tru).map((task) => task)
      if (validResults.length) {
        message.info(t('dataset.add.batch.success', { count: validResults.length }))
      } else {
        message.info(t('dataset.add.failure'))
      }
    }
  }, [results])

  const batchHandle = useCallback(() => {
    if (editing) {
      Modal.confirm({
        content: t('dataset.add.editing.tip'),
        onOk: () => batch({ pid: id }),
      })
    } else {
      batch({ pid: id })
    }
  }, [editing, id])

  const Btns = (
    <Button disabled={!items.length} type="primary" size="large" onClick={batchHandle}>
      {t('common.action.import')}
    </Button>
  )

  return (
    <Card className={s.container} title={t('breadcrumbs.dataset.add')} extra={Btns}>
      {items.length && items.some((item) => item.dup) ? <Alert type="error" message={t('dataset.add.name.duplicated')} /> : null}
      <AddList style={{ marginBottom: 20 }} />
      <AddSelector />
      <FormatDetailModal title={t('dataset.add.form.tip.format.detail')} visible={visible} onCancel={() => showFormatDetail(false)} />
      <Prompt when={editing || !!items.length} message={t('dataset.add.leave.page.prompt')} />
    </Card>
  )
}

export default BatchAdd
