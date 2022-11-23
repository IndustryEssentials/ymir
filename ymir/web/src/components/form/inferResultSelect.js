import { Alert, Button, Checkbox, Col, Form, Row, Select, Tooltip } from 'antd'
import { connect } from 'dva'
import { useCallback, useEffect, useState } from 'react'

import t from '@/utils/t'
import { INFER_DATASET_MAX_COUNT, INFER_CLASSES_MAX_COUNT } from '@/constants/common'
import useFetch from '@/hooks/useFetch'
import ModelSelect from './modelSelect'
import DatasetSelect from './datasetSelect'
import { useHistory } from 'umi'
import { humanize } from '@/utils/number'

const sameConfig = (config, config2) => {
  return JSON.stringify(config2) === JSON.stringify(config)
}
const sameConfigs = (config, configs) => {
  return configs.some((item) => sameConfig(item, config))
}

const ConfigSelect = ({ value, configs = [], onChange = () => {} }) => {
  const [options, setOptions] = useState([])

  useEffect(() => {
    const opts = configs.map((item, index) => {
      const title = [...item.model, JSON.stringify(item.config)].join('\n')
      return {
        value: index,
        label: (
          <Tooltip color={'blue'} title={title}>
            {item.name}
          </Tooltip>
        ),
        config: item,
      }
    })
    setOptions(opts)
  }, [configs])

  useEffect(() => {
    if (value) {
      change(
        value,
        options.filter((opt) => value.includes(opt.value)),
      )
    }
  }, [options])

  const change = (values) => {
    onChange(
      values,
      values.map((index) => options[index]),
    )
  }

  return <Checkbox.Group value={value} options={options} onChange={change}></Checkbox.Group>
}

const InferResultSelect = ({ pid, form, value, onChange = () => {} }) => {
  const history = useHistory()
  const [models, setModels] = useState([])
  const [datasets, setDatasets] = useState([])
  const [testingDatasets, setTestingDatasets] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [configs, setConfigs] = useState([])
  const [selectedConfigs, setSelectedConfigs] = useState([])
  const [inferTasks, fetchInferTask] = useFetch('task/queryInferTasks', [])
  const [fetched, setFetched] = useState(false)
  const [selectedTasks, setSelectedTasks] = useState([])
  const [tasks, setTasks] = useState([])
  const selectedStages = Form.useWatch('stage', form)

  useEffect(() => {
    setTasks(inferTasks)
    setFetched(true)
  }, [inferTasks])

  useEffect(() => {
    const stages = selectedStages?.map(([model, stage]) => stage) || []
    if (stages.length) {
      fetchInferTask({ stages })
    } else {
      setTasks([])
      setFetched(false)
    }
    setSelectedDatasets([])
    form.setFieldsValue({ dataset: undefined, config: undefined })
  }, [selectedStages])

  useEffect(() => {
    if (datasets.length === 1 && datasets[0].assetCount <= INFER_DATASET_MAX_COUNT) {
      form.setFieldsValue({ dataset: datasets })
    }
    setConfigs([])
    form.setFieldsValue({ config: undefined })
  }, [datasets])

  useEffect(() => {
    form.setFieldsValue({ config: configs.length === 1 ? [0] : undefined })
  }, [configs])

  useEffect(() => {
    const testingDatasets = tasks.map(({ parameters: { dataset_id } }) => dataset_id)
    const crossDatasets = testingDatasets.filter((dataset) => {
      const targetTasks = tasks.filter(({ parameters: { dataset_id } }) => dataset_id === dataset)
      return selectedStages.every(([model, stage]) => targetTasks.map(({ parameters: { model_stage_id } }) => model_stage_id).includes(stage))
    })
    setDatasets([...new Set(crossDatasets)])
  }, [tasks])

  useEffect(() => {
    const configs = tasks
      .filter(({ parameters: { dataset_id } }) => (selectedDatasets ? selectedDatasets.includes(dataset_id) : true))
      .reduce((prev, { config, parameters: { model_id, model_stage_id } }) => {
        const stageName = getStageName([model_id, model_stage_id])
        return sameConfigs(
          config,
          prev.map(({ config }) => config),
        )
          ? prev.map((item) => {
              sameConfig(item.config, config) && item.model.push(stageName)
              return item
            })
          : [...prev, { config, model: [stageName] }]
      }, [])
    setConfigs(configs.map((config, index) => ({ ...config, name: `config${index + 1}` })))
  }, [tasks, selectedDatasets])

  useEffect(() => {
    form.setFieldsValue({ config: configs.map((_, index) => index) })
  }, [configs])

  useEffect(() => {
    const selected = []
    selectedStages?.forEach(([model, selectedStage]) => {
      selectedDatasets.forEach((did) => {
        const dtask = tasks.filter(({ parameters: { dataset_id, model_stage_id: stage } }) => dataset_id === did && stage === selectedStage)
        selectedConfigs.forEach(({ config: sconfig, name }) => {
          const ctask = dtask.find(({ config }) => sameConfig(config, sconfig))
          ctask && selected.push({ ...ctask, configName: name })
        })
      })
    })
    setSelectedTasks(selected)
  }, [tasks, selectedConfigs])

  useEffect(() => {
    onChange({
      tasks: selectedTasks,
      models,
      datasets: testingDatasets,
    })
  }, [selectedTasks])

  function getStageName([model, stage]) {
    const m = models.find((md) => md.id === model)
    let s = {}
    if (m) {
      s = m.stages.find((sg) => sg.id === stage)
    }
    return m && s ? `${m.name} ${m.versionName} ${s.name}` : ''
  }

  function modelChange(values, options = []) {
    // setSelectedStages(values)
    setModels(options.map(([opt]) => opt?.model))
  }

  function datasetChange(values, options = []) {
    setSelectedDatasets(values)
    setTestingDatasets(options.map(({ dataset }) => dataset))
  }

  function configChange(values, options = []) {
    setSelectedConfigs(options.map((opt) => (opt ? opt.config : null)))
  }

  const filterDatasets = useCallback(
    (all) => {
      return all
        .filter(({ id }) => datasets.includes(id))
        .map((ds) => ({
          ...ds,
          disabled: ds.assetCount > INFER_DATASET_MAX_COUNT,
        }))
    },
    [datasets],
  )

  const filterModels = (models) =>
    models.map((model) => ({
      ...model,
      disabled: model.keywords.length > INFER_CLASSES_MAX_COUNT,
    }))

  const goInfer = useCallback(() => {
    const mids = selectedStages?.map(String)?.join('|')
    const query = selectedStages?.length ? `?mid=${mids}` : ''
    history.push(`/home/project/${pid}/inference${query}`)
  }, [selectedStages])

  const renderInferBtn = (
    <div className={fetched && !datasets.length ? 'error' : ''} style={{ lineHeight: '32px' }}>
      {t('task.infer.diagnose.tip')}
      <Button size="small" onClick={goInfer}>
        {t('common.action.inference')}
      </Button>
    </div>
  )

  return (
    <>
      <Form.Item
        name="stage"
        label={t('model.diagnose.label.model')}
        help={<Alert style={{ marginBottom: 20 }} message={t('model.diagnose.metrics.tip.exceed.classes', { max: INFER_CLASSES_MAX_COUNT })} type="warning" />}
        rules={[{ required: true }, { type: 'array', max: 5 }]}
        extra={renderInferBtn}
      >
        <ModelSelect pid={pid} multiple filters={filterModels} onChange={modelChange} />
      </Form.Item>
      {datasets.length ?
      <Form.Item
        name="dataset"
        help={
          <Alert
            style={{ marginBottom: 20 }}
            message={t('model.diagnose.metrics.tip.exceed.assets', { max: humanize(INFER_DATASET_MAX_COUNT, 0) })}
            type="warning"
          />
        }
        // hidden={!datasets.length}
        label={t('model.diagnose.label.testing_dataset')}
        rules={[{ required: true }, { type: 'array', max: 5 }]}
      >
        <DatasetSelect pid={pid} mode="multiple" filters={filterDatasets} onChange={datasetChange} />
      </Form.Item> : null }
      <Form.Item name="config" hidden={!configs.length} label={t('model.diagnose.label.config')} rules={[{ required: true }, { type: 'array', max: 5 }]}>
        <ConfigSelect configs={configs} onChange={configChange} />
      </Form.Item>
    </>
  )
}

const props = (state) => {
  return {
    allModels: state.model.allModels,
  }
}

export default connect(props, null)(InferResultSelect)
