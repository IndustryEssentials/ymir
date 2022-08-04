import Datasets from '@/components/dataset/list'
import ListHOC from "./components/list.hoc"

const List = ListHOC(Datasets)

export default () => <List />
