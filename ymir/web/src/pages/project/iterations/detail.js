import React, { useEffect, useState } from "react"
import { useSelector } from 'umi'

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import Panel from "./detail.panel"

import s from "./index.less"

const filterExsit = list => list.filter(item => item)

function Detail({ project = {} }) {

  const [settings, setSettings] = useState([])
  const [intermediations, setIntermediations] = useState([])
  const [models, setModels] = useState([])
  const [_, getIteration] = useFetch('iteration/getIteration')
  const iteration = useSelector(({ iteration }) => iteration.iteration)
  const iid = project.currentIteration?.id

  useEffect(() => {
    project.id && iid && getIteration({ pid: project.id, id: iid, more: true })
  }, [project.id, iid])

  useEffect(() => {
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
      <Panel list={settings} title={t('project.iteration.detail.settings.title')} />
      { intermediations.length ? <Panel list={intermediations} title={t('project.iteration.detail.intermediations.title')} /> : null }
      { models.length ? <Panel list={models} title={t('project.iteration.detail.models.title')} type='model' /> : null }
    </div>
  )
}

export default Detail
