import { Cascader, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import { percent } from '@/utils/number'
import useFetch from '../../hooks/useFetch'


const ModelSelect = ({ pid, value, allModels, onChange = () => { }, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [models, setModels] = useState([])
  const [_, getModels] = useFetch('model/queryAllModels')

  useEffect(() => {
    getModels(pid)
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

  function generateOptions() {
    console.log('models:', models)
    const opts = models.map(model => {
      const name = `${model.name} ${model.versionName}`
      const map = model.map
      return {
        label: <span>{name} (mAP: <strong title={map}>{percent(map)}</strong></span>,
        model,
        value: model.id,
        children: model.stages.map(stage => ({ 
          label: `${name} ${stage.name}`, 
          value: stage.id, 
        })),
      }
    })
    setOptions(opts)
  }

  function labelRender(labels, options) {
    console.log('render: ', labels, options)
    return labels.join('-')
  }

  return (
    <Cascader value={value} {...resProps} onChange={onChange} options={options} displayRender={labelRender} allowClear></Cascader>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(ModelSelect)
