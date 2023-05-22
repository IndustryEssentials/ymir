import { Button, Card } from 'antd'
import { FC, useState, useEffect } from 'react'
import { useSelector } from 'umi'
import { ImportItem } from './add/'
import t from '@/utils/t'
import AddList from './add/AddList'
import AddSelector from './add/AddSelector'

import s from './add.less'

type Props = {}
const BatchAdd: FC<Props> = ({}) => {
  const [key, setKey] = useState(0)
  const [items, setItems] = useState<ImportItem[]>([])

  useEffect(() => {
    setKey(Math.random())
  }, [items])
  return (
    <Card className={s.container} title={t('breadcrumbs.dataset.add')}>
      <AddList items={items} />
      <AddSelector key={key} confirm={setItems} />
    </Card>
  )
}
export default BatchAdd
