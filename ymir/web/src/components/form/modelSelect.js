import { Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import { percent } from '@/utils/number'


const ModelSelect = ({ pid, value, allModels, onChange = () => { }, getModels, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [models, setModels] = useState([])

  useEffect(() => {
    fetchModels()
  }, [])

  useEffect(() => {
    if (options.length) {
      if (value) {
        onChange(value, resProps.mode ? options.filter(opt => value.includes(opt.value)) : options.find(opt => opt.value === value))
      }
    }
  }, [options])

  useEffect(() => {
    setModels(allModels)
  }, [allModels])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  useEffect(() => {
    generateOptions()
  }, [models])

  function fetchModels() {
    getModels(pid)
  }

  function generateOptions() {
    const opts = models.map(model => {
      return {
        label: <Row gutter={10} wrap={false}>
          <Col flex={1}>{model.name} {model.versionName}</Col>
          <Col>mAP: <strong title={model.map}>{percent(model.map)}</strong></Col>
        </Row>,
        model,
        value: model.id,
      }
    })
    setOptions(opts)
  }

  return (
    <Select value={value} {...resProps} onChange={onChange} options={options} allowClear></Select>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}
const actions = (dispatch) => {
  return {
    getModels(pid) {
      return dispatch({
        type: 'model/queryAllModels',
        payload: pid,
      })
    }
  }
}
export default connect(props, actions)(ModelSelect)
