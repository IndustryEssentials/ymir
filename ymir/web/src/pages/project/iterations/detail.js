import React, { useEffect, useState } from 'react'

import t from '@/utils/t'
import Panel from './detail.panel'
import { getSteps } from '@/constants/iteration'

import s from './index.less'

const filterExsit = (list) => list.filter(({ id: notEmpty }) => notEmpty)

function Detail({ project = {} }) {
  const [settings, setSettings] = useState([])
  const [intermediations, setIntermediations] = useState([])
  const [models, setModels] = useState([])
  const iid = project.currentIteration?.id
  const [iteration, setIteration] = useState(null)

  useEffect(() => {
    project.id && iid && setIteration(project.currentIteration)
  }, [project, iid])

  useEffect(() => {
    const { wholeMiningSet, testSet } = iteration || {}
    const steps = getSteps()
    const slist = filterExsit([
      {
        label: 'project.mining_set',
        id: wholeMiningSet || project.miningSet?.id,
      },
      {
        label: 'project.test_set',
        id: testSet || project.testSet?.id,
      },
    ])
    if (!iteration) {
      setSettings(slist)
      setIntermediations([])
      setModels([])
      return
    }
    const ilist = filterExsit(
      steps.slice(0, 4).map((step) => {
        const istep = iteration.steps.find((st) => st.name === step.value)
        return { label: step.act, id: istep.resultId }
      }),
    )
    const mlist = filterExsit([{ label: '', id: iteration.steps[4].resultId }])
    setSettings(slist)
    setIntermediations(ilist)
    setModels(mlist)
  }, [iteration, project])

  return (
    <div className={s.detail}>
      <Panel list={settings} title={t('project.iteration.detail.settings.title')} />
      {intermediations.length ? <Panel list={intermediations} title={t('project.iteration.detail.intermediations.title')} /> : null}
      {models.length ? <Panel list={models} title={t('project.iteration.detail.models.title')} type="model" /> : null}
    </div>
  )
}

export default Detail
