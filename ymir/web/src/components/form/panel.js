import { Col, Row } from "antd"
import { ArrowDownIcon, ArrowRightIcon } from '@/components/common/icons'
import s from './panel.less'
import { useEffect, useState } from "react"

const Panel = ({ hasHeader = true, toogleVisible = true, visible, setVisible = () => { }, label = '', children }) => {
  const [vis, setVis] = useState(false)
  useEffect(() => {
    setVis(visible)
  }, [visible])

  useEffect(() => {
    setVisible(vis)
  }, [vis])

  return (
    <div className='panel'>
      {hasHeader ? <Row className='header' onClick={() => setVis(!vis)}>
        <Col flex={1} className='title'>{label}</Col>
        {toogleVisible ?
          <Col className='foldBtn'>{vis ? <span><ArrowDownIcon /></span> : <span><ArrowRightIcon /></span>}</Col>
          : null}
      </Row> : null}
      <div className={s.content} hidden={toogleVisible && hasHeader ? !vis : false}>
        {children}
      </div>
    </div>
  )
}

export default Panel
