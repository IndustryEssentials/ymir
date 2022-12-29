import { FC } from 'react'
import { Form, Input } from 'antd'
const { Search } = Input
type Props = {
  onSearch?: (value: string) => void
}
const Name: FC<Props> = ({ onSearch }) => {
  const search = (value: string) => {
    onSearch && onSearch(value)
  }
  return <Search placeholder="dataset/model name" allowClear onSearch={search} />
}

export default Name
