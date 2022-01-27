import { Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import t from '@/utils/t'
import { percent } from '../../../utils/number'


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
    const same = models.filter(model => model.keywords.toString() === keywords.toString()) || []
    const inter = models.filter(model => {
      const kws = model.keywords
      return kws.toString() !== keywords.toString() && kws.some(kw => keywords.includes(kw))
    })
    const diff = models.filter(model => model.keywords.every(kw => !keywords.includes(kw))) || []
    setModels([...same, ...inter, ...diff])
  }, [keywords])

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
    const opts = models.map(model => {
      return {
        label: <Row gutter={10} wrap={false}>
          <Col flex={1}>{model.name}</Col>
          <Col>mAP: <strong title={model.map}>{percent(model.map)}</strong></Col>
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
