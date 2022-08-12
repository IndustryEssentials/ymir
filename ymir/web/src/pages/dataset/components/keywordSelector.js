import { Cascader, Col, Row, Select } from "antd"
import t from "@/utils/t"
import { useEffect, useState } from "react"

import useFetch from '@/hooks/useFetch'

const initKeywords = [
  { value: 'keywords', list: [], },
  { value: 'cks', list: [], },
  { value: 'tags', list: [], }
]

const KeywordSelector = ({ value, onChange, dataset = {} }) => {
  const [keywords, setKeywords] = useState(initKeywords)
  const [currentType, setCurrentType] = useState(initKeywords[0].value)
  const [selected, setSelected] = useState([0, []])
  const [{ cks, tags }, getCK] = useFetch('dataset/getCK', { cks: {}, tags: {} })

  useEffect(() => {
    if (!dataset.id) {
      return
    }
    getCK({ pid: dataset.projectId, id: dataset.id })
    generateKeywords(initKeywords[0].value, dataset.keywords.map(keyword => ({ keyword })))
  }, [dataset])

  useEffect(() => {
    generateKeywords(initKeywords[1].value, cks.keywords)
  }, [cks, tags])

  useEffect(() => {
    generateKeywords(initKeywords[2].value, tags.keywords)
  }, [tags])

  useEffect(() => {
    onChange({ type: currentType, selected })
  }, [selected])

  useEffect(() => {
    setSelected([])
  }, [currentType])

  function generateKeywords(type, kws = []) {
    console.log('type, kws:', type, kws)
    const parse = (list = []) => list.map(({ keyword, children }) => ({
      value: keyword,
      label: keyword,
      children: children?.length ? parse(children) : undefined,
    }))
    return setKeywords(keywords => keywords.map(({ value, list }) => (value === type ? { value: type, list: parse(kws) } : { value, list })))
  }

  const renderKeywords = (type) => {
    const { list = [] } = keywords.find(({ value }) => value === type)
    return type !== 'keywords' ? renderCk(list) : <Select
      showSearch
      value={selected}
      mode="multiple"
      allowClear
      style={{ width: 160 }}
      onChange={setSelected}
      placeholder={t('dataset.assets.keyword.selector.types.placeholder')}
      filterOption={(input, option) => option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0}
      options={list}
    ></Select>
  }

  const renderCk = (list = []) => {
    return <Cascader value={selected} multiple allowClear onChange={setSelected} options={list} placeholder={t('dataset.assets.keyword.selector.types.placeholder')} />
  }


  return (
    <Row gutter={10}>
      <Col style={{ width: 150 }}>
        <Select
          style={{ width: '100%' }}
          defaultValue={currentType}
          onChange={setCurrentType}
          options={keywords.map(({ value }) => ({ value, label: t(`dataset.assets.keyword.selector.types.${value}`) }))}
        />
      </Col>
      <Col flex={1}>
        {renderKeywords(currentType)}
      </Col>
    </Row>
  )
}

export default KeywordSelector
