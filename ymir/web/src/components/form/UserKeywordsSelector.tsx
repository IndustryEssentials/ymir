import { Col, Row, Select, SelectProps } from 'antd'
import { FC, useEffect, useState } from 'react'
import { DefaultOptionType } from 'antd/lib/select'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { useDebounce } from 'ahooks'
import { KeywordObjectType, KeywordsQueryParams } from '@/services/keyword.d'

type OptionType = DefaultOptionType & {
  value: string
  aliases?: string[]
}
type Props = SelectProps

const UserKeywordsSelector: FC<Props> = (props) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const [queryName, setQueryName] = useState('')
  const debonceQueryName = useDebounce(queryName, {
    wait: 800,
  })
  const {
    data: keywordResult,
    run: getKeywords,
    loading,
  } = useRequest<YStates.List<KeywordObjectType>, [KeywordsQueryParams]>('keyword/getKeywords', {
    loading: false,
  })

  useEffect(() => {
    fetchKeywords()
  }, [])

  useEffect(() => {
    if (!debonceQueryName) {
      return
    }
    fetchKeywords(debonceQueryName)
  }, [debonceQueryName])

  useEffect(() => {
    if (keywordResult) {
      generateOptions(keywordResult.items)
    }
  }, [keywordResult])

  function generateOptions(keywords: KeywordObjectType[] = []) {
    const opts = keywords.map((keyword) => ({
      label: (
        <Row>
          <Col flex={1}>{keyword.name}</Col>
        </Row>
      ),
      aliases: keyword.aliases,
      value: keyword.name,
    }))
    setOptions(opts)
  }

  const fetchKeywords = (name?: string) => getKeywords({ q: name, limit: 10 })

  return (
    <Select
      showArrow
      placeholder={t('task.train.form.keywords.label')}
      {...props}
      mode="tags"
      onSearch={setQueryName}
      filterOption={false}
      options={options}
      loading={loading}
    ></Select>
  )
}

export default UserKeywordsSelector
