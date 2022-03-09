import { Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import t from '@/utils/t'
import { percent } from '../../../utils/number'


const ModelSelect = ({ pid, value, allModels, keywords = [], onChange = () => { }, getModels, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [models, setModels] = useState([])

  useEffect(() => {
    fetchModels()
  }, [])

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

  useEffect(() => {
    if (allModels.length && keywords.length) {
      const same = allModels.filter(model => model.keywords.toString() === keywords.toString()) || []
      const inter = allModels.filter(model => {
        const kws = model.keywords
        return kws.toString() !== keywords.toString() && kws.some(kw => keywords.includes(kw))
      })
      const diff = allModels.filter(model => model.keywords.every(kw => !keywords.includes(kw))) || []
      setModels([...same, ...inter, ...diff])
    }
  }, [keywords])

  async function fetchModels() {
    await getModels(pid)
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

const props = (state) => {
  return {
    models: state.model.allModels,
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
