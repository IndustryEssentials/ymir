import { ChangeEvent, FC } from 'react'
import { Input } from 'antd'
import type { SearchProps } from 'antd/lib/input'
import { useDebounceFn } from 'ahooks'

import t from '@/utils/t'

const { Search } = Input

const Name: FC<SearchProps> = (props) => {
  return <Search {...props} placeholder={t('common.search.result.name')} allowClear />
}

export default Name
