import { Checkbox, Col, Form, Row, Select, Tooltip } from 'antd'
import { connect } from 'dva'
import { useCallback, useEffect, useState } from 'react'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import ModelSelect from './modelSelect'
import DatasetSelect from './datasetSelect'

const sameConfig = (config, config2) => {
  return JSON.stringify(config2) === JSON.stringify(config)
}
const sameConfigs = (config, configs) => {
  return configs.some(item => sameConfig(item, config))
}

const ConfigSelect = ({ configs = [], onChange = () => { } }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    const opts = configs.map(({ config, model }, index) => {
      const title = [...model, JSON.stringify(config)].join('\n')
      return {
        value: index,
        label: <Tooltip color={'blue'} title={title}>config{index + 1}</Tooltip>,
        config
      }
    })
    setOptions(opts)
  }, [configs])

  const change = (values) => {
    onChange(values, values.map(index => options[index]))
  }

  return <Checkbox.Group options={options} onChange={change}></Checkbox.Group>
}

const InferResultSelect = ({ pid, form, value, onChange = () => { } }) => {
  const [selectedStages, setSelectedStages] = useState([])
  const [models, setModels] = useState([])
  const [datasets, setDatasets] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [configs, setConfigs] = useState([])
  const [selectedConfigs, setSelectedConfigs] = useState([])
  const [inferTasks, fetchInferTask] = useFetch('task/queryInferTasks', [])
  const [selectedTasks, setSelectedTasks] = useState([])
  const [tasks, setTasks] = useState([])

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
    setSelectedDatasets([])
    form.setFieldsValue({ dataset: [], config: []})
  }, [selectedStages])

  useEffect(() => {
    const testingDatasets = tasks.map(({ parameters: { dataset_id } }) => dataset_id)
    const crossDatasets = testingDatasets.filter(dataset => {
      const targetTasks = tasks.filter(({ parameters: { dataset_id } }) => dataset_id === dataset)
      return selectedStages.every(([model, stage]) => targetTasks.map(({ parameters: { model_stage_id } }) => model_stage_id).includes(stage))
    })
    setDatasets(crossDatasets)
  }, [tasks])

  useEffect(() => {
    const configs = tasks
      .filter(({ parameters: { dataset_id } }) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true))
      .reduce((prev, { config, parameters: { model_id, model_stage_id } }) => {
        const stageName = getStageName([model_id, model_stage_id])
        return sameConfigs(config, prev.map(({ config }) => config)) ?
          prev.map(item => {
            sameConfig(item.config, config) && item.model.push(stageName)
            return item
          }) :
          [...prev, { config, model: [stageName] }]
      }, [])
    setConfigs(configs)
  }, [tasks, selectedDatasets])

  useEffect(() => {
    const selected = tasks
      .filter(({ parameters: { dataset_id }, config }) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true)
        && (selectedConfigs.length ? sameConfigs(config, selectedConfigs) : true))
    const unique = selected.reduce((prev, task) => {
      return prev.some(({ parameters: { dataset_id }, config }) =>
        dataset_id === task.dataset_id && sameConfig(config, task.parameters.config)) ?
        prev : [...prev, task]
    }, [])
    setSelectedTasks(unique)
  }, [tasks, selectedConfigs])

  useEffect(() => {
    onChange({
      tasks: selectedTasks,
    })
  }, [selectedTasks])

  function getStageName([model, stage]) {
    const m = models.find(md => md.id === model)
    let s = {}
    if (m) {
      s = m.stages.find(sg => sg.id === stage)
    }
    console.log('s:', s)
    return m && s ? `${m.name} ${m.versionName} ${s.name}` : ''
  }

  function modelChange(values, options) {
    setSelectedStages(values)
    setModels(options.map(([{ model }]) => model))
  }

  function datasetChange(values) {
    setSelectedDatasets(values)
  }

  function configChange(values, options) {
    setSelectedConfigs(options.map(({ config }) => config))
  }

  const filterDatasets = useCallback((all) => {
    return all.filter(({ id }) => datasets.includes(id))
  }, [datasets])

  return (
    <>
      <Form.Item name='stage' label={t('model.diagnose.label.model')} rules={[{ required: true }]}>
        <ModelSelect pid={pid} multiple onChange={modelChange} />
      </Form.Item>
      {datasets.length ?
        <Form.Item name='dataset' label={t('model.diagnose.label.testing_dataset')} rules={[{ required: true }]}>
          <DatasetSelect pid={pid} mode='multiple' filters={filterDatasets} onChange={datasetChange} />
        </Form.Item>
        : null}
      {configs.length ?
        <Form.Item name='config' label={t('model.diagnose.label.config')} rules={[{ required: true }]}>
          <ConfigSelect configs={configs} onChange={configChange} />
        </Form.Item>
        : null}
    </>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(InferResultSelect)
