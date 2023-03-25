import { FC } from 'react'
import Datasets from '@/components/dataset/List'
import ListHOC from './components/ListHoc'

const List = ListHOC(Datasets)

const DatasetList: FC = () => <List />

export default DatasetList
