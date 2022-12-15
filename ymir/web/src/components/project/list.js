import { List } from "antd"
import Item from "@/components/project/list/Item"

export const Lists = ({ projects = [], more = "" }) => {
  return <List className="list" dataSource={projects} renderItem={item => <Item project={item} more={more} />} />
}
