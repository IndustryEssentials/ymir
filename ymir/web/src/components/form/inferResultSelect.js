import { Checkbox, Col, Row, Select } from 'antd'
import { connect } from 'dva'
import { useEffect, useState } from 'react'

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

const ConfigSelect = ({ tasks = [], onChange = () => { } }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    const opts = tasks.reduce((prev, task) => {
      const config = task.config
      return sameConfigs(config, prev) ? prev : prev.concat(config)
    }, []).map((config, index) => ({ value: index, label: `config${index + 1}`, config: config }))
    setOptions(opts)
  }, [tasks])

  return <Checkbox.Group options={options} onChange={onChange}></Checkbox.Group>
}

const InferResultSelect = ({ pid, value, onChange = () => { } }) => {
  const [selectedStages, setSelectedStages] = useState([])
  const [datasets, setDatasets] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [configs, setConfigs] = useState([])
  const [selectedConfigs, setSelectedConfigs] = useState([])
  const [tasks, fetchInferTask] = useFetch('task/queryTask')
  const [selectedTasks, setSelectedTasks] = useState([])
  const [inferResult, setInferResult] = useState([])

  useEffect(() => {
    const stages = selectedStages.map(([model, stage]) => stage)
    fetchInferTask({ stages })
  }, [selectedStages])

  useEffect(() => {
    const selected = tasks
      ?.filter(({ dataset_ids: [dataset], config }) => (selectedDatasets ? selectedDatasets.includes(dataset) : true)
        && (selectedConfigs.length ? sameConfigs(config, selectedConfigs) : true))
    setSelectedTasks(selected)
  }, [selectedDatasets, selectedConfigs])

  function modelChange(values) {
    setSelectedStages(values)
  }

  function datasetChange(values) {
    setSelectedDatasets(values)
  }

  function configChange(values, options) {
    setSelectedConfigs(options.map(option => option.config))
  }

  function filterDatasets(datasets) {
    const testingDatasets = tasks.map(({ dataset_ids }) => dataset_ids[0])
    return datasets.filter(({ id }) => testingDatasets.includes(id))
  }

  return (
    <>
      <ModelSelect pid={pid} multiple onChange={modelChange} />
      { tasks?.length ? <DatasetSelect pid={pid} mode='multiple' filters={filterDatasets} onChange={datasetChange} /> : null }
      { selectedTasks?.length ? <ConfigSelect data={selectedTasks} onChange={configChange} /> : null }
    </>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(InferResultSelect)
