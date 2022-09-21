import { Cascader, ConfigProvider } from 'antd'
import { useSelector } from 'umi'
import { useEffect, useState } from 'react'

import { percent } from '@/utils/number'
import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import EmptyStateModel from '@/components/empty/model'

const ModelSelect = ({ pid, value, onlyModel, changeByUser, onChange = () => { }, filters, ...resProps }) => {
  const models = useSelector(state => state.model.allModels)
  const [ms, setMS] = useState(null)
  const [options, setOptions] = useState([])
  const [_, getModels] = useFetch('model/queryAllModels')

  useEffect(() => {
    pid && getModels(pid)
  }, [pid])

  useEffect(() => {
    if (options.length) {
      if (value && !changeByUser) {
        if (resProps.multiple) {
          const opts = options.filter(opt => value.some(([model]) => opt.model.id === model)).map(opt => [opt, opt.value])
          onChange(value, opts)
        } else {
          const opt = options.find(opt => opt?.model?.id === value[0])
          if (!opt) {
            return
          }
          const stage = value[1] || opt.model?.recommendStage
          onChange(value, [opt, stage])
        }
      }
    }
  }, [options])

  useEffect(() => {
    if (value && !value[1]) {
      const model = models.find(md => md.id === value[0])
      if (model) {
        setMS([value[0], model.recommendStage])
      }
    }
  }, [options])

  useEffect(() => {
    setMS(value)
  }, [value])

  useEffect(() => {
    generateOptions()
  }, [models, filters])

  function generateOptions() {
    const mds = filters ? filters(models) : models
    const opts = mds.map(model => {
      const name = `${model.name} ${model.versionName}`
      const childrenNode = onlyModel ? {} : {
        children: model.stages.map(stage => ({
          label: ` ${stage.name} (mAP:${percent(stage.map)}) ${stage.id === model.recommendStage ? t('common.recommend') : ''}`,
          value: stage.id,
        }))
      }
      return {
        label: name,
        model,
        value: model.id,
        ...childrenNode,
      }
    })
    setOptions(opts)
  }

  function filter(input, path) {
    return path.some(({ label = '' }) => label.toLowerCase().indexOf(input.toLowerCase()) > -1)
  }

  return (
    <ConfigProvider renderEmpty={() => <EmptyStateModel />}>
      <Cascader value={ms} onChange={onChange} options={options}
        showCheckedStrategy={Cascader.SHOW_CHILD} showSearch={{ filter }}
        placeholder={t('task.train.form.model.placeholder')}
        allowClear {...resProps}></Cascader>
    </ConfigProvider>
  )
}

export default ModelSelect
