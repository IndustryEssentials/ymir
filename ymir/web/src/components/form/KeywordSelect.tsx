import { Col, Row, Select, SelectProps } from 'antd'
import { FC, useEffect, useState } from 'react'
import { DefaultOptionType } from 'antd/lib/select'

import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import { List } from '@/models/typings/common.d'

type KeywordType = {
  name: string
  aliases?: string[]
}
type OptionType = DefaultOptionType & {
  value: string
  aliases?: string[]
}
type Props = SelectProps & {
  keywords?: string[]
  filter?: (kws: OptionType[]) => OptionType[]
}

const KeywordSelect: FC<Props> = ({ value, onChange = () => {}, keywords, filter = (x) => x, ...resProps }) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const { data: keywordResult, run: getKeywords } = useRequest<List<KeywordType>, [{ limit?: number }]>('keyword/getKeywords')

  useEffect(() => {
    if (keywords) {
      generateOptions(keywords.map((keyword) => ({ name: keyword })))
    } else {
      getKeywords({ limit: 9999 })
    }
  }, [keywords])

  useEffect(() => {
    if (options.length) {
      if (value) {
        onChange(
          value,
          options.filter((opt) => value.includes(opt.value)),
        )
      }
    }
  }, [options])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  useEffect(() => {
    if (keywordResult) {
      generateOptions(keywordResult.items)
    }
  }, [keywordResult])

  function generateOptions(keywords: KeywordType[] = []) {
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
      {...resProps}
      mode="multiple"
      value={value}
      filterOption={(value, option) => !!option && [option.value, ...(option.aliases || [])].some((key) => key.indexOf(value) >= 0)}
      options={filter(options)}
      onChange={onChange}
    ></Select>
  )
}

export default KeywordSelect
