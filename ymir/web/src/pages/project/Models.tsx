import { FC } from 'react'
import Models from '@/components/model/List'
import ListHOC from './components/ListHoc'

const List = ListHOC(Models)

const ModelList: FC = () => <List />

export default ModelList
