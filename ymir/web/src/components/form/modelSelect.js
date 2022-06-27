import { Cascader, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

import { percent } from '@/utils/number'
import t from '@/utils/t'
import useFetch from '../../hooks/useFetch'


const ModelSelect = ({ pid, value, allModels, onChange = () => { }, ...resProps }) => {
  const [options, setOptions] = useState([])
  const [models, setModels] = useState([])
  const [_, getModels] = useFetch('model/queryAllModels')

  useEffect(() => {
    pid && getModels(pid)
  }, [pid])

  useEffect(() => {
    if (options.length) {
      if (value) {
        onChange(value, resProps.multiple ? options.filter(opt => value.includes(opt.value)) : options.find(opt => opt.value === value))
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
    const opts = models.map(model => {
      const name = `${model.name} ${model.versionName}`
      return {
        label: name,
        model,
        value: model.id,
        children: model.stages.map(stage => ({
          label: ` ${stage.name} (mAP:${percent(stage.map)}) ${stage.id === model.recommendStage ? t('common.recommend') : ''}`,
          value: stage.id,
        })),
      }
    })
    setOptions(opts)
  }

  function labelRender(labels, options) {
    return <span>{labels.map(label => label)}</span>
  }

  function filter(input, path) {
    return path.some(({ label = '' }) => label.toLowerCase().indexOf(input.toLowerCase()) > -1)
  }

  return (
    <Cascader value={value} {...resProps} onChange={onChange} options={options} 
    displayRender={labelRender} showCheckedStrategy={Cascader.SHOW_CHILD} showSearch={{ filter }} allowClear></Cascader>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(ModelSelect)
