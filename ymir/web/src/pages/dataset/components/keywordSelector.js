import { Cascader, Col, Row, Select } from "antd"
import t from "@/utils/t"
import { useEffect, useState } from "react"


const KeywordSelector = ({ value, onChange, dataset = {} }) => {
  const [keywords, setKeywords] = useState([])
  const [currentType, setCurrentType] = useState(0)
  const [selected, setSelected] = useState([0, []])

  useEffect(() => {
    if (!dataset.id) {
      return
    }
    const lists = generateKeywordList(dataset)
    setKeywords(lists)
  }, [dataset])

  useEffect(() => {
    onChange(selected)
  }, [selected])

  function keywordsChange(value) {
    console.log('keyword change: ', value)
    setSelected([currentType, value])
  }

  function generateKeywordList(dataset) {
    const k = dataset.keywords
    const bt = dataset.boxTags || []
    const ck = dataset.ck || []
    const list = [
      { value: 'k', list: k, },
      { value: 'ck', list: ck, },
      { value: 'bt', list: bt, }
    ]
    return list
  }

  const renderKeywords = ({ value: type, list = [] }) => {
    return type === 'ck' ? renderCk(list) : <Select
      showSearch
      mode="multiple"
      allowClear
      style={{ width: 160 }}
      onChange={keywordsChange}
      placeholder={t('dataset.assets.keyword.selector.types.placeholder')}
      filterOption={(input, option) => option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0}
      options={list.map(keyword => ({
        value: keyword,
        label: keyword
      }))}
    ></Select>
  }

  const renderCk = (ck = {}) => {
    console.log('ck:', ck)
    const list = Object.keys(ck).map(key => {
      const children = ck[key] || []
      return {
        value: key,
        label: key,
        children: Object.keys(children),
      }
    })
    return <Cascader multiple allowClear options={list} placeholder={t('dataset.assets.keyword.selector.types.placeholder')} />
  }


  return (
    <Row gutter={10}>
      <Col style={{ width: 150 }}>
        <Select
          style={{ width: '100%'}}
          defaultValue={currentType}
          onChange={(value) => { console.log('type select: ', value); setCurrentType(value)}}
          options={keywords.map(({ value }, index) => ({ value: index, label: t(`dataset.assets.keyword.selector.types.${value}`) }))}
        />
      </Col>
      <Col flex={1}>
        {keywords.length ? renderKeywords(keywords[currentType]) : null}
      </Col>
    </Row>
  )
}

export default KeywordSelector
