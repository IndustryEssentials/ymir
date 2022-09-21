import React, { useEffect, useState } from "react"

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import Panel from "./detail.panel"

import s from "./index.less"

const filterExsit = list => list.filter(item => item)

function Detail({ project }) {

  const [settings, setSettings] = useState([])
  const [intermediations, setIntermediations] = useState([])
  const [models, setModels] = useState([])
  const [iteration, getIteration] = useFetch('iteration/getIteration')
  const iid = project.currentIteration?.id

  useEffect(() => {
    project.id && iid && getIteration({ pid: project.id, id: iid, more: true })
  }, [project, iid])

  useEffect(() => {
    console.log('project:', project)
    if (!project?.id) {
      return
    }
    setSettings([project.miningSet, project.testSet])
    if (!iteration) {
      return
    }
    const {
      wholeMiningDataset,
      trainUpdateDataset,
      miningDataset,
      miningResultDataset,
      labelDataset,
      testDataset,
      trainingModel,
    } = iteration
    setSettings(filterExsit([wholeMiningDataset, testDataset]))
    setIntermediations(filterExsit([miningDataset, miningResultDataset, labelDataset, trainUpdateDataset]))
    setModels(filterExsit([trainingModel]))
  }, [iteration, project])

  return (
    <div className={s.detail}>
      <Panel list={settings} title='迭代设置' />
      { intermediations.length ? <Panel list={intermediations} title='中间数据' /> : null }
      { models.length ? <Panel list={models} title='结果模型' type='model' /> : null }
    </div>
  )
}

export default Detail
