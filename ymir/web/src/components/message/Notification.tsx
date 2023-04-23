import { FC, useEffect } from 'react'
import { notification } from 'antd'
import { useSelector } from 'umi'
import BaseItem, { Props } from './BaseItem'
import t from '@/utils/t'

const key = 'message'

const NotificationItem: FC<Props> = ({ total, title, content, go, unread }) => {
  useEffect(() => {
    if (!title || !content) {
      return notification.close(key)
    }
    notification.open({
      key,
      message: title,
      description: (
        <div style={{ cursor: 'pointer' }}>
          {content}
          <span onClick={(e) => e.stopPropagation()} style={{ display: 'block', textAlign: 'right' }}>
            {console.log('total:', total)}
            {t('message.unread.label', { count: total - 1 })}
          </span>
        </div>
      ),
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
  }, [title, content, total])
  return <></>
}

const Item = BaseItem(NotificationItem)
const Notification: FC = () => {
  const message = useSelector(({ message }) => message.latest)
  useEffect(() => {
    if (!message) {
      notification.close(key)
    }
  }, [message])
  return <Item message={message} />
}

export default Notification
