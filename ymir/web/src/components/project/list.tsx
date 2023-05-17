import { FC, ReactChild } from 'react'
import { List } from 'antd'
import Item from '@/components/project/list/Item'
import { Project } from '@/constants'

type Props = {
  projects?: Project[]
  more?: ReactChild
}
export const Lists: FC<Props> = ({ projects = [], more = '' }) => {
  return <List className="list" dataSource={projects} renderItem={(item) => <Item project={item} more={more} />} />
}
