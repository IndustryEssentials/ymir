import { Select } from 'antd'
import { connect } from 'umi'
import { useEffect, useState } from 'react'
import t from '@/utils/t'

const DatasetSelect = ({ pid, filter = [], value, datasets = [], onChange = () => { }, getDatasets, ...resProps }) => {

  useEffect(() => {
    pid && fetchDatasets()
  }, [pid])

  function fetchDatasets() {
    getDatasets(pid)
  }

  return (
    <Select
      placeholder={t('task.train.form.training.datasets.placeholder')}
      filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
      onChange={onChange}
      showArrow
      {...resProps}
    >
      {datasets.filter(ds => !filter.includes(ds.id)).map(item =>
        <Option value={item.id} key={item.name}>
          {item.name} {item.versionName}(assets: {item.assetCount})
        </Option>
      )}
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
        payload: {pid, force},
      })
    }
  }
}
export default connect(props, actions)(DatasetSelect)
