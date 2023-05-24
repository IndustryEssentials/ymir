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

type Props = {}
const Selectors = {
  [Types.LOCAL]: Local,
  [Types.COPY]: Copy,
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
      <Form>
        <Form.Item label={t('dataset.add.form.type.label')}>
          <TypeSelector
            onChange={(type) => {
              console.log('hello: type', type)
              setCurrent(type)
            }}
          />
        </Form.Item>
        {Selector ? <Selector /> : null}
      </Form>
    </div>
  )
}
export default AddSelector
