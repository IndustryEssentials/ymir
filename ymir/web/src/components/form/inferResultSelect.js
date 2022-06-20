import { Checkbox, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useCallback, useEffect, useState } from 'react'

import useFetch from '@/hooks/useFetch'
import ModelSelect from './modelSelect'
import DatasetSelect from './datasetSelect'

const sameConfigs = (config, configs) => {
  return configs.some(item => {
    const itemStr = JSON.stringify(item)
    const configStr = JSON.stringify(config)
    return itemStr === configStr
  })
}

const ConfigSelect = ({ configs = [], onChange = () => { } }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    const opts = configs.map((config, index) => ({ value: index, label: `config${index + 1}`, config }))
    setOptions(opts)
  }, [configs])

  const change = (values) => {
    onChange(values, values.map(index => options[index]))
  }

  return <Checkbox.Group options={options} onChange={change}></Checkbox.Group>
}

const InferResultSelect = ({ pid, value, onChange = () => { } }) => {
  const [selectedStages, setSelectedStages] = useState([])
  const [datasets, setDatasets] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [configs, setConfigs] = useState([])
  const [selectedConfigs, setSelectedConfigs] = useState([])
  const [inferTasks, fetchInferTask] = useFetch('task/queryInferTasks', [])
  const [selectedTasks, setSelectedTasks] = useState([])
  const [tasks, setTasks] = useState([])
  const [inferResult, setInferResult] = useState([])

  useEffect(() => {
    setTasks(inferTasks)
  }, [inferTasks])

  useEffect(() => {
    const stages = selectedStages.map(([model, stage]) => stage)
    if (stages.length) {
      fetchInferTask({ stages })
    } else {
      setTasks([])
    }
  }, [selectedStages])

  useEffect(() => {
    const selected = tasks
      .filter(({ parameters:{ dataset_id }}) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true))
      .map(({ config }) => config)
      setConfigs(selected)
  }, [selectedDatasets])

  useEffect(() => {
    const selected = tasks
      .filter(({ parameters:{ dataset_id }, config }) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true)
        && (selectedConfigs.length ? sameConfigs(config, selectedConfigs) : true))
    setSelectedTasks(selected)
  }, [selectedConfigs])

  useEffect(() => {
    onChange({
      tasks: selectedTasks,
    })
  }, [selectedTasks])

  function modelChange(values) {
    console.log('model change values:', values)
    setSelectedStages(values)
  }

  function datasetChange(values) {
    setSelectedDatasets(values)
  }

  function configChange(values, options) {
    setSelectedConfigs(options.map(({ config }) => config))
  }

  const filterDatasets = useCallback((datasets) => {
    console.log('filter datasets tasks:', tasks)
    const testingDatasets = tasks.map(({ parameters: { dataset_id } }) => dataset_id)
    return datasets.filter(({ id }) => testingDatasets.includes(id))
  }, [tasks])

  return (
    <>
      <ModelSelect pid={pid} multiple onChange={modelChange} />
      {tasks.length ? <DatasetSelect pid={pid} mode='multiple' filters={filterDatasets} onChange={datasetChange} /> : null}
      {configs.length ? <ConfigSelect configs={configs} onChange={configChange} /> : null}
    </>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(InferResultSelect)
