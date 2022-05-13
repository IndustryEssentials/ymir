import { useCallback, useEffect, useState } from "react"

import t from '@/utils/t'
import { Dropdown, Menu, Space } from "antd"
import { ArrowDownIcon } from "@/components/common/icons"

const useDynamicColumn = () => {
  const [keywords, setKeywords] = useState([])
  const [selected, setSelected] = useState(null)
  const [options, setOptions] = useState([])
  const change = ({ key }) => setSelected(key)

  useEffect(() => {
    if (keywords.length) {
      setOptions([
        ...keywords.map(label => ({ key: label, label: label })),
        { key: '', label: t('common.everage') }
      ])
    }
  }, [keywords])

  useEffect(() => {
    setSelected(options.length ? options[0].key : null)
  }, [options])

  const render = useCallback((metrics = {}) => {
    const everage = metrics.ci_averaged_evaluation || {}
    const kwMetrics = metrics.ci_evaluations|| {}
    const result = selected === '' ? everage : kwMetrics[selected]
    return result?.ap
  }, [selected])


  const menus = <Menu items={options} onClick={change} />
  const title = <Dropdown overlay={menus}>
    <Space>
      {selected === '' ? t('common.everage') : selected}
      <ArrowDownIcon />
    </Space>
  </Dropdown>
  const column = {
    title,
    dataIndex: 'metrics',
    render,
    ellipsis: {
      showTitle: true,
    },
  }
  return { column, render, setKeywords }
}

export default useDynamicColumn
