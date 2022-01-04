import { Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import t from '@/utils/t'


const ModelSelect = ({ value, keywords = [], onChange = () => { }, getModels, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [models, setModels] = useState([])

  useEffect(() => {
    fetchModels()
  }, [])

  useEffect(() => {
    if (options.length === 1) {
      value = options[0].value
    }
  }, [options])

  useEffect(() => {
    generateOptions()
  }, [models])

  useEffect(() => {
    setModels(models.map(model => ({ ...model, hidden: keywords.length ? model.keywords.toString() !== keywords.toString() : false })))
  }, [keywords])

  useEffect(() => {
    const opt = options.find(opt => opt.value === value) || {}
    onChange(opt.value, opt.model)
  }, [value])

  async function fetchModels() {
    const params = {
      offset: 0,
      limit: 100000,
    }
    const result = await getModels(params)
    if (result?.items) {
      setModels(result.items)
    }
  }

  function generateOptions() {
    const opts = models.filter(model => !model.hidden).map(model => {
      return {
        label: <Row gutter={10} wrap={false}>
          <Col flex={1}>{model.name}</Col>
          <Col>mAP: <strong>{model.map}</strong></Col>
          <Col>{t('model.column.target')}: {model.keywords.join(',')}</Col>
        </Row>,
        model,
        value: model.id,
      }
    })
    setOptions(opts)
  }

  return (
    <Select value={value} {...resProps} onChange={(value, option) => onChange(value, option?.model)} options={options} allowClear></Select>
  )
}

const actions = (dispatch) => {
  return {
    getModels(payload) {
      return dispatch({
        type: 'model/getModels',
        payload,
      })
    }
  }
}
export default connect(null, actions)(ModelSelect)
