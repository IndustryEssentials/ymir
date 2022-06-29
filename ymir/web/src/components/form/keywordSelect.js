import { Cascader, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useCallback, useEffect, useState } from 'react'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'


const KeywordSelect = ({ value, onChange = () => { }, data = [], keywords, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [_, getKeywords] = useFetch('keyword/getKeywords')

  useEffect(() => {
    getKeywords({ limit: 9999 })
  }, [])

  useEffect(() => {
    if (options.length) {
      if (value) {
        onChange(value, resProps.mode ? options.filter(opt => value.includes(opt.value)) : options.find(opt => opt.value === value))
      }
    }
  }, [options])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  useEffect(() => {
    generateOptions()
  }, [keywords])

  function generateOptions() {
    const opts = keywords.map(keyword => ({
      label: <Row><Col flex={1}>{keyword.name}</Col></Row>,
      aliases: keyword.aliases,
      value: keyword.name,
    }))
    setOptions(opts)
  }

  return (
    <Select mode="multiple" showArrow
      placeholder={t('task.train.form.keywords.label')}
      filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}
      options={options}
    ></Select>
  )
}

const props = (state) => {
  return {
    keywords: state.keyword.keywords.items,
  }
}

export default connect(props, null)(KeywordSelect)
