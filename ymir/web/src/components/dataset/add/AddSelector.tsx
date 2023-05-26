import { Col, Form, Row } from 'antd'
import { FC, useState, useEffect } from 'react'
import { Types } from './AddTypes'
import Local from './Local'
import Net from './Net'
import Path from './Path'
import TypeSelector from './TypeSelector'
import s from '../add.less'
import t from '@/utils/t'
import { useSelector } from 'umi'
import Copy from './Copy'
import Public from './Public'
import { formLayout } from '@/config/antd'

type Props = {}
const Selectors = {
  [Types.LOCAL]: Local,
  [Types.COPY]: Copy,
  [Types.INTERNAL]: Public,
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
      <Row className={s.type}>
        <Col {...formLayout.labelCol}>{t('dataset.add.form.type.label')}</Col>
        <Col {...formLayout.wrapperCol}>
          <TypeSelector
            onChange={(type) => {
              console.log('hello: type', type)
              setCurrent(type)
            }}
          />
        </Col>
      </Row>
      {Selector ? <Selector /> : null}
    </div>
  )
}
export default AddSelector
