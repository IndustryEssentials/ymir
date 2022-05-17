import { Select } from 'antd'
import { connect } from 'umi'
import { useEffect, useState } from 'react'
import t from '@/utils/t'

const DatasetSelect = ({ pid, filter = [], filterGroup = [], filters, value, datasets = [], onChange = () => { }, getDatasets, ...resProps }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    pid && fetchDatasets()
  }, [pid])

  useEffect(() => {
    let selected = null
    if (value) {
      if (resProps.mode) {
        selected = options.filter(opt => value.includes(opt.value))
      } else {
        selected = options.find(opt => value === opt.value)
      }
      onChange(value, selected)
    }
  }, [options])

  useEffect(() => {
    const dss = filters ? filters(datasets) : datasets
    const opts = dss.filter(ds => !filter.includes(ds.id) && !filterGroup.includes(ds.groupId)).map(item => {
      return {
        label: <>{item.name} {item.versionName}(assets: {item.assetCount})</>,
        dataset: item,
        value: item.id,
      }
    })
    setOptions(opts)
  }, [filters, datasets])

  function fetchDatasets() {
    getDatasets(pid, true)
  }

  return (
    <Select
      value={value}
      placeholder={t('task.train.form.training.datasets.placeholder')}
      onChange={onChange}
      showArrow
      allowClear
      options={options}
      {...resProps}
    >
    </Select>
  )
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
