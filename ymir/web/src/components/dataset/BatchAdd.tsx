import { Button, Card, Form, message, Space } from 'antd'
import { FC, useEffect } from 'react'
import t from '@/utils/t'
import AddList from './add/AddList'
import AddSelector from './add/AddSelector'
import FormatDetailModal from '@/components/dataset/FormatDetailModal'

import s from './add.less'
import { useHistory, useParams, useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import { Task } from '@/constants'

const BatchAdd: FC = () => {
  const { id } = useParams<{ id: string }>()
  const history = useHistory()
  const { formatVisible: visible, items } = useSelector(({ dataset }) => dataset.importing)
  const { run: showFormatDetail } = useRequest<null, [boolean]>('dataset/showFormatDetail', { loading: false })
  const { data: results, run: batch } = useRequest<(Task | null)[], [{ pid: string }]>('task/batchAdd')

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

  const Btns = (
    <Button disabled={!items.length} type="primary" size="large" onClick={() => batch({ pid: id })}>
      {t('common.action.import')}
    </Button>
  )

  return (
    <Card className={s.container} title={t('breadcrumbs.dataset.add')} extra={Btns}>
      <AddList />
      <AddSelector />
      <FormatDetailModal title={t('dataset.add.form.tip.format.detail')} visible={visible} onCancel={() => showFormatDetail(false)} />
    </Card>
  )
}

export default BatchAdd
