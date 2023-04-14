import { CSSProperties, FC } from 'react'
import { List } from 'antd'

import { CloseOutlined } from '@ant-design/icons'
import { Props } from './BaseItem'

const closeStyle: CSSProperties = {
  position: 'absolute',
  top: 24,
  right: 24,
}

const Item: FC<Props> = ({ title, content, go, unread }) => {
  return (
    <List.Item onClick={go} style={{ cursor: 'pointer', padding: '24px', position: 'relative' }}>
      <List.Item.Meta title={title} description={content} />
      <span style={closeStyle} onClick={unread}>
        <CloseOutlined />
      </span>
    </List.Item>
  )
}

export default Item
