import { Col, Row, Select, SelectProps } from 'antd'
import { FC, useEffect, useState } from 'react'
import { DefaultOptionType } from 'antd/lib/select'
import { useSelector } from 'umi'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { List } from '@/models/typings/common.d'
import { ClassObject } from '@/constants'

type OptionType = DefaultOptionType & {
  value: string
  aliases?: string[]
}
type Props = SelectProps

const UserKeywordsSelector: FC<Props> = (props) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const keywords = useSelector(({ keyword }) => keyword.allKeywords)
  const { run: getAllKeywords, loading } = useRequest<List<ClassObject>>('keyword/getAllKeywords', {
    loading: false,
  })

  useEffect(() => {
    getAllKeywords()
  }, [])

  useEffect(() => {
    keywords && generateOptions(keywords)
  }, [keywords])

  function generateOptions(keywords: ClassObject[] = []) {
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

  return (
    <Select
      showArrow
      placeholder={t('task.train.form.keywords.label')}
      {...props}
      mode="tags"
      filterOption={(value, option) => !!option && [option.value, ...(option.aliases || [])].some((key) => key.indexOf(value) >= 0)}
      options={options}
      loading={loading}
    ></Select>
  )
}

export default UserKeywordsSelector
