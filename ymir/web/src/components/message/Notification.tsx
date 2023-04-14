import { FC, useEffect } from 'react'
import { notification } from 'antd'
import { useSelector } from 'umi'
import BaseItem, { Props } from './BaseItem'

const key = 'message'

const Notification: FC = () => {
  const message = useSelector(({ message }) => message.latest)
  const Item = BaseItem(NotificationItem)
  return <Item message={message} />
}

const NotificationItem: FC<Props> = ({ title, content, go, unread }) => {
  useEffect(() => {
    if (!title || !content) {
      return notification.close(key)
    }
    notification.open({
      key,
      message: title,
      description: <div style={{ cursor: 'pointer' }}>{content}</div>,
      onClick: () => {
        go()
        notification.close(key)
      },
      duration: null,
      placement: 'bottomRight',
      onClose: () => {
        unread()
      },
    })
  }, [title, content])
  return <></>
}

export default Notification
