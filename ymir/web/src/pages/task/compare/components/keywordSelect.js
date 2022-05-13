import { useCallback, useEffect, useState } from "react"

import t from '@/utils/t'
import { Dropdown, Menu, Space } from "antd"
import { ArrowDownIcon } from "@/components/common/icons"

const KeywordSelect = ({ value, keywords, onChange = () => {} }) => {
  const [selected, setSelected] = useState(null)
  const [options, setOptions] = useState([])
  const change = ({ key }) => setSelected(key)
  useEffect(() => {
    if (keywords?.length) {
      setOptions([
        ...keywords.map(label => ({ key: label, label: label })),
        { key: '', label: t('common.everage') }
      ])
    } else {
      setOptions([])
    }
  }, [keywords])

  useEffect(() => {
    value && setSelected(value)
  }, [value])

  useEffect(() => {
    onChange(selected)
  }, [selected])

  useEffect(() => {
    setSelected(options.length ? options[0].key : null)
  }, [options])

  const menus = <Menu items={options} onClick={change} />

  return <>
    <span>{t('dataset.column.keyword')}:</span>
    <Dropdown overlay={menus}>
      <Space>
        {selected === '' ? t('common.everage') : selected}
        <ArrowDownIcon />
      </Space>
    </Dropdown>
  </>
}

export default KeywordSelect
