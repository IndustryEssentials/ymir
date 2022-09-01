import { Cascader, Col, Row, Select } from "antd"
import { useParams } from "umi"
import t from "@/utils/t"
import { useEffect, useState } from "react"

import useFetch from '@/hooks/useFetch'

const initKeywords = [
  { value: 'keywords', list: [], },
  { value: 'cks', list: [], },
  { value: 'tags', list: [], }
]

const KeywordSelector = ({ value, onChange, dataset = {} }) => {
  const { id: pid } = useParams()
  const [keywords, setKeywords] = useState(initKeywords)
  const [currentType, setCurrentType] = useState(initKeywords[0].value)
  const [selected, setSelected] = useState([])
  const [[{ cks, tags }], getCK] = useFetch('dataset/getCK', [{ cks: {}, tags: {} }])

  useEffect(() => {
    !value?.length && setSelected([])
  }, [value])

  useEffect(() => {
    if (!dataset.id) {
      return
    }
    getCK({ pid: dataset.projectId, ids: [dataset.id] })
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
    return setKeywords(keywords => keywords.map((item) => ({
      ...item,
      list: item.value === type ? kws : item.list
    })))
  }

  const renderKeywords = (type) => {
    const { list = [] } = keywords.find(({ value }) => value === type) || {}
    return type !== 'keywords' ? renderCk(list) : renderKw(list)
  }

  const renderKw = (list = []) => <Select
    showSearch
    value={selected}
    mode="multiple"
    fieldNames={{ label: 'keyword', value: 'keyword' }}
    allowClear
    style={{ width: 160 }}
    onChange={setSelected}
    placeholder={t('dataset.assets.keyword.selector.types.placeholder')}
    options={list}
  />

  const renderCk = (list = []) => <Cascader
    value={selected}
    multiple
    allowClear
    expandTrigger="hover"
    fieldNames={{ label: 'keyword', value: 'keyword' }}
    onChange={setSelected}
    options={list}
    displayRender={value => value.join('/')}
    placeholder={t('dataset.assets.keyword.selector.types.placeholder')}
  />


  return (
    <Row gutter={10}>
      <Col style={{ width: 150 }}>
        <Select
          style={{ width: '100%' }}
          value={currentType}
          onChange={setCurrentType}
          options={keywords.map(({ value }) => ({
            value,
            label: t(`dataset.assets.keyword.selector.types.${value}`)
          }))}
        />
      </Col>
      <Col flex={1}>
        {renderKeywords(currentType)}
      </Col>
    </Row>
  )
}

export default KeywordSelector
