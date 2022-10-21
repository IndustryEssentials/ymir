import { Col, ConfigProvider, Row, Select } from 'antd'
import { useSelector } from 'umi'
import { useEffect, useState } from 'react'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import EmptyState from '@/components/empty/dataset'

const defaultLabelRender = ({ name, versionName, assetCount }) => {
  const label = `${name} ${versionName}(assets: ${assetCount})`
  return name ? <span title={label}>{label}</span> : null
}

const DatasetSelect = ({
  pid, filter = [], allowEmpty, filterGroup = [],
  filters, value, onChange = () => { }, renderLabel = defaultLabelRender,
  onReady = () => { },
  extra, changeByUser, ...resProps
}) => {
  const [options, setOptions] = useState([])
  const datasets = useSelector(({ dataset }) => dataset.allDatasets)
  const [_, getDatasets] = useFetch('dataset/queryAllDatasets', [], true)
  const [val, setVal] = useState(value)

  useEffect(() => setVal(value), [value])

  useEffect(() => {
    pid && fetchDatasets()
  }, [pid])

  useEffect(() => {
    onReady(datasets)
  }, [datasets])

  useEffect(() => {
    let selected = null
    if (options.length && value && !changeByUser) {
      if (resProps.mode) {
        selected = options.filter(opt => value.includes(opt.value))
      } else {
        selected = options.find(opt => value === opt.value)
      }
      if (selected) {
        onChange(value, selected)
      } else {
        onChange(undefined, null)
        setVal(undefined)
      }
    }
  }, [options])

  useEffect(() => {
    const needReload = datasets.some(ds => ds.needReload)
    if (needReload) {
      fetchDatasets()
    }
  }, [datasets])

  useEffect(() => {
    let dss = filters ? filters(datasets) : datasets
    dss = allowEmpty ? dss : filterEmptyAsset(dss)
    const opts = dss.filter(ds => !filter.includes(ds.id) && !filterGroup.includes(ds.groupId)).map(item => {
      return {
        label: renderLabel(item),
        dataset: item,
        value: item.id,
      }
    })
    setOptions(opts)
  }, [filters, datasets])

  async function fetchDatasets() {
    await getDatasets({ pid, force: true })
  }

  function filterEmptyAsset(datasets) {
    return datasets.filter(ds => ds.assetCount)
  }

  const select = <ConfigProvider renderEmpty={() => <EmptyState />}>
    <Select
      value={val}
      placeholder={t('task.train.form.training.datasets.placeholder')}
      onChange={onChange}
      showArrow
      allowClear
      showSearch
      options={options}
      filterOption={(input, option) => option.dataset.name.toLowerCase().indexOf(input.toLowerCase()) >= 0}
      {...resProps}
    >
    </Select>
  </ConfigProvider>

  return extra ? <Row gutter={20} wrap={false}><Col flex={1}>{select}</Col><Col>{extra}</Col></Row> : select
}

export default DatasetSelect
