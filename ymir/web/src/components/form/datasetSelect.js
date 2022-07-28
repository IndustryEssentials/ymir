import { Col, ConfigProvider, Row, Select } from 'antd'
import { connect } from 'umi'
import { useEffect, useState } from 'react'
import t from '@/utils/t'

import EmptyState from '@/components/empty/dataset'

const defaultLabelRender = item => <>{item.name} {item.versionName}(assets: {item.assetCount})</>

const DatasetSelect = ({
  pid, filter = [], allowEmpty, filterGroup = [],
  filters, value, datasets = [], onChange = () => { }, renderLabel = defaultLabelRender,
  extra, changeByUser, getDatasets, ...resProps
}) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    console.log('pid:', pid)
    pid && fetchDatasets()
  }, [pid])

  useEffect(() => {
    let selected = null
    if (value && !changeByUser) {
      if (resProps.mode) {
        selected = options.filter(opt => value.includes(opt.value))
      } else {
        selected = options.find(opt => value === opt.value)
      }
      onChange(value, selected)
    }
  }, [options])

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

  function fetchDatasets() {
    getDatasets(pid, true)
  }

  function filterEmptyAsset(datasets) {
    return datasets.filter(ds => ds.assetCount)
  }

  const select = <ConfigProvider renderEmpty={() => <EmptyState />}>
    <Select
      value={value}
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

const props = (state) => {
  return {
    datasets: state.dataset.allDatasets,
  }
}
const actions = (dispatch) => {
  return {
    getDatasets(pid, force) {
      return dispatch({
        type: 'dataset/queryAllDatasets',
        payload: { pid, force },
      })
    }
  }
}
export default connect(props, actions)(DatasetSelect)
