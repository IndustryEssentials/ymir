import { Col, Row } from 'antd'
import { FC, useState, useEffect } from 'react'
import { Types } from './AddTypes'
import Local from './Local'
import Net from './Net'
import Path from './Path'
import TypeSelector from './TypeSelector'
import s from '../add.less'
import { useSelector } from 'umi'

type Props = {}
const Selectors = {
  [Types.LOCAL]: Local,
  [Types.COPY]: Local,
  [Types.INTERNAL]: Local,
  [Types.NET]: Net,
  [Types.PATH]: Path,
}
const AddSelector: FC<Props> = () => {
  const [current, setCurrent] = useState(Types.LOCAL)
  const [Selector, setSelector] = useState<FC>()

  useEffect(() => {
    setSelector(() => Selectors[current])
  }, [current])

  return (
    <div className={s.selector}>
      <Row>
        <Col>
          <TypeSelector
            onChange={(type) => {
              console.log('hello: type', type)
              setCurrent(type)
            }}
          />
        </Col>
        <Col flex={1}>{Selector ? <Selector /> : null}</Col>
      </Row>
    </div>
  )
}
export default AddSelector
