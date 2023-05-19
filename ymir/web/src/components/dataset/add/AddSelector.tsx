import { Button, Col, Row } from 'antd'
import { FC, useState, useEffect } from 'react'
import { ImportItem, ImportSelectorProps } from '.'
import { Types } from './AddTypes'
import Local from './Local'
import Net from './Net'
import Path from './Path'
import TypeSelector from './TypeSelector'
type Props = {
  confirm: (items: ImportItem[]) => void
}
const Selectors = {
  [Types.LOCAL]: Local,
  [Types.COPY]: Local,
  [Types.INTERNAL]: Local,
  [Types.NET]: Net,
  [Types.PATH]: Path,
}
const AddSelector: FC<Props> = ({ confirm }) => {
  const [current, setCurrent] = useState(Types.LOCAL)
  const [items, setItems] = useState<ImportItem[]>([])
  const [Selector, setSelector] = useState<FC<ImportSelectorProps>>()

  useEffect(() => {
    setSelector(() => Selectors[current])
  }, [current])

  const ok = () => {
    confirm(items)
  }

  return (
    <div>
      <Row>
        <Col>
          <TypeSelector
            onChange={(type) => {
              console.log('hello: type', type)
              setCurrent(type)
            }}
          />
        </Col>
        <Col flex={1}>{Selector ? <Selector onChange={(items) => setItems(items)} /> : null}</Col>
      </Row>
      <Button type="primary" onClick={ok}>
        Confirm
      </Button>
    </div>
  )
}
export default AddSelector
