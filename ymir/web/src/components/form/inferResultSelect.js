import { Checkbox, Col, Form, Row, Select, Tooltip } from 'antd'
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
    const opts = configs.map((config, index) => ({
      value: index,
      label: <Tooltip color={'blue'} title={JSON.stringify(config)}>config{index + 1}</Tooltip>,
      config
    }))
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
      .filter(({ parameters: { dataset_id } }) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true))
      .reduce((prev, { config }) => {
        return sameConfigs(config, prev) ? prev : [...prev, config]
      }, [])
    setConfigs(selected)
  }, [selectedDatasets])

  useEffect(() => {
    const selected = tasks
      .filter(({ parameters: { dataset_id }, config }) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true)
        && (selectedConfigs.length ? sameConfigs(config, selectedConfigs) : true))
    setSelectedTasks(selected)
  }, [selectedConfigs])

  useEffect(() => {
    onChange({
      tasks: selectedTasks,
    })
  }, [selectedTasks])

  function modelChange(values) {
    setSelectedStages(values)
  }

  function datasetChange(values) {
    setSelectedDatasets(values)
  }

  function configChange(values, options) {
    setSelectedConfigs(options.map(({ config }) => config))
  }

  const filterDatasets = useCallback((datasets) => {
    const testingDatasets = tasks.map(({ parameters: { dataset_id } }) => dataset_id)
    const crossDatasets = testingDatasets.filter(dataset => {
      const targetTasks = tasks.filter(({ parameters: { dataset_id }}) => dataset_id === dataset)
      return selectedStages.map(([model, stage]) => model).every(model => targetTasks.map(({ parameters: { model_stage_id }})=> model_stage_id).includes(model))
    })
    return datasets.filter(({ id }) => crossDatasets.includes(id))
  }, [tasks])

  return (
    <Form layout='vertical'>
      <Form.Item label={'model'}>
        <ModelSelect pid={pid} multiple onChange={modelChange} />
      </Form.Item>
      {tasks.length ?
        <Form.Item label={'testing dataset'}>
          <DatasetSelect pid={pid} mode='multiple' filters={filterDatasets} onChange={datasetChange} />
        </Form.Item>
        : null}
      {configs.length ?
        <Form.Item label={'parameters config'}>
          <ConfigSelect configs={configs} onChange={configChange} />
        </Form.Item>
        : null}
    </Form>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(InferResultSelect)
