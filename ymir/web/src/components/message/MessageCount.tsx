import { FC, useEffect } from 'react'
import { Popover, PopoverProps } from 'antd'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import t from '@/utils/t'
import List from './List'
import { NotifyIcon } from '../common/Icons'

const MessageCount: FC<PopoverProps> = (props) => {
  const unreadCount = useSelector(({ message }) => message.total)
  const { run: getUnreadCount } = useRequest('message/getUnreadCount', {
    loading: false,
  })
  const title = <h3>{t('message.list.title', {count: unreadCount})}</h3>
  useEffect(() => {
    getUnreadCount()
  }, [])

  return (
    <Popover trigger={'click'} placement={'topRight'} overlayStyle={{ borderRadius: '10px' }} title={title} {...props} content={<List />}>
      <span style={{ color: '#fff' }}>
        <NotifyIcon /> {unreadCount}
      </span>
    </Popover>
  )
}

export default MessageCount
