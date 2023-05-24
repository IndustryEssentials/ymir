import { Card } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'
import AddList from './add/AddList'
import AddSelector from './add/AddSelector'
import FormatDetailModal from '@/components/dataset/FormatDetailModal'

import s from './add.less'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'

const BatchAdd: FC = () => {
  const visible = useSelector(({ dataset }) => dataset.importing.formatVisible)
  const { run: showFormatDetail } = useRequest<null, [boolean]>('dataset/showFormatDetail', { loading: false })
  return (
    <Card className={s.container} title={t('breadcrumbs.dataset.add')}>
      <AddList />
      <AddSelector />
      <FormatDetailModal title={t('dataset.add.form.tip.format.detail')} visible={visible} onCancel={() => showFormatDetail(false)} />
    </Card>
  )
}

export default BatchAdd
