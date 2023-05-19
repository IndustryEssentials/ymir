import { Button } from 'antd'
import { FC, useState, useEffect } from 'react'
import { useSelector } from 'umi'
import { ImportItem } from './add/'
import AddList from './add/AddList'
import AddSelector from './add/AddSelector'
type Props = {}
const BatchAdd: FC<Props> = ({}) => {
  const [key, setKey] = useState(0)
  const [items, setItems] = useState<ImportItem[]>([])

  useEffect(() => {
    setKey(Math.random())
  }, [items])
  return (
    <>
      <AddList items={items} />
      {/* <div><Button type='primary' onClick={() => setKey(Math.random())}>Add</Button></div> */}
      <AddSelector key={key} confirm={setItems} />
    </>
  )
}
export default BatchAdd
