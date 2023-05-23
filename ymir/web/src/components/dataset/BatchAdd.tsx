import { Card } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'
import AddList from './add/AddList'
import AddSelector from './add/AddSelector'

import s from './add.less'

const BatchAdd: FC = () => (
  <Card className={s.container} title={t('breadcrumbs.dataset.add')}>
    <AddList />
    <AddSelector />
  </Card>
)

export default BatchAdd
