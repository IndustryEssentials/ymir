import Datasets from '@/components/dataset/List'
import ListHOC from "./components/list.hoc"

const List = ListHOC(Datasets)

export default () => <List />
