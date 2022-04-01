import { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import Rect from './rect'
import s from './guide.less'
import { Button, Popover } from 'antd'

const Step = ({ elem, show = false }) => {
  const [visible, setVisible] = useState(show)
  const [pos, setPos] = useState({
    x: 0, 
    y: 0,
    width: 0,
    height: 0,
  })

  useEffect(() => {
    setVisible(show)
  }, [show])

  useEffect(() => {
    if (visible) {
      window.document.body.style.height = '100%'
      window.document.body.style.overflow = 'hidden'
    } else {
      window.document.body.style.height = ''
      window.document.body.style.overflow = ''
    }
  }, [visible])

  useEffect(() => {
    if (elem) {
      const { x, y, width, height } = elem.getBoundingClientRect()
      setPos({
        x, y, width, height,
      })
    }
    
  }, [elem])

  function close () {
    setVisible(false)
  }

  return visible ? (
    <>
      <Popover content={'hello'} trigger='click' visible={true}>
        <div style={{position: 'fixed', left: pos.x, top: pos.y, width: pos.width, height: pos.height }}></div>
      </Popover>
      <Rect x={pos.x} y={pos.y} width={pos.width} height={pos.height} visible={true} />
      <Button type='link' onClick={() => close()} style={{ position: 'fixed', right: 20, top: 20, zIndex: 6 }}>X</Button>
    </>
  ) : null
}

export default Step
