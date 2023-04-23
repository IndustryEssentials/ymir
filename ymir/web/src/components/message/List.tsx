import { Message } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { List as AList, ListProps } from 'antd'
import { FC, useEffect } from 'react'
import { useSelector } from 'umi'
import DefaultEmpty from '../empty/Default'
import BaseItem from './BaseItem'
import Item from './Item'

const List: FC<ListProps<Message>> = (props) => {
  const { fresh, messages } = useSelector(({ message }) => message)
  const { run: getMessages } = useRequest('message/getMessages')
  const ListItem = BaseItem(Item)

  useEffect(() => getMessages({}), [])

  useEffect(() => {
    fresh && getMessages({})
  }, [fresh])

  return messages.length ? (
    <AList style={{ width: 280, margin: '-12px -16px' }} {...props} dataSource={messages} renderItem={(message) => <ListItem message={message} />}></AList>
  ) : (
    <DefaultEmpty />
  )
}

export default List
