import { FC } from 'react'
import { Input } from 'antd'
import type { SearchProps } from 'antd/lib/input'

const { Search } = Input

const Name: FC<SearchProps> = (props) => <Search {...props} placeholder="dataset/model name" allowClear />

export default Name
