import { useEffect, useState } from 'react'
import { useSelector } from 'umi'
import { Space } from 'antd'

import { Stages, StageList } from '@/constants/iteration'
import useFetch from '@/hooks/useFetch'

import Fusion from "@/components/task/fusion"

const Action = (Comp) => {
  function Generate(props) { return <Comp {...props} /> }
  return Generate
}

const StepAction = ({ stages, iteration, project, prevIteration }) => {
  const [updated, updateIteration] = useFetch('iteration/updateIteration')
  const result = useSelector(({ dataset, model }) => {
    const isModel = currentContent?.value === Stages.training
    const res = isModel ? model.model : dataset.dataset
    return res[currentContent?.result] || {}
  })

  const comps = {
    [Stages.prepareMining]: {
      comp: Action(Fusion), query: {
        did: project.miningSet?.id,
        merging: project.miningSet.id || 0,
        strategy: project.miningStrategy,
        chunk: project.chunkSize || undefined,
      },
    },
    [Stages.mining]: {
      comp: Action(Fusion), query: {
        did: iteration.miningSet,
        mid: prevIteration.id ? [prevIteration.model, null] : project.modelStage,
      },
    },
    [Stages.labelling]: {
      comp: Action(Fusion), query: {
        did: iteration.miningResult,
      },
    },
    [Stages.merging]: {
      comp: Action(Fusion), query: {
        did: prevIteration.trainUpdateSet || project.trainSetVersion,
        mid: iteration.labelSet,
      },
    },
    [Stages.training]: {
      comp: Action(Fusion), query: {
        did: iteration.trainUpdateSet,
        test: iteration.testSet,
      },
    },
    [Stages.next]: {
      comp: Action(Fusion), query: {}
    },
  }
  const fixedQuery = {
    iterationId: iteration.id,
    currentStage: iteration.currentStage,
    from: 'iteration'
  }
  const [currentContent, setCurrentContent] = useState(null)
  const [CurrentAction, setCurrentAction] = useState(() => {})

  useEffect(() => {
    console.log('comps[iteration.currentStage]:', comps[iteration.currentStage])
    setCurrentAction(comps[iteration.currentStage].comp)
  }, [iteration?.currentStage])

  useEffect(() => {

    console.log('CurrentAction:', CurrentAction)
  }, [CurrentAction])

  useEffect(() => {
    console.log('stages:', stages, currentContent)
    if (!stages.length) {
      return
    }
    const targetStage = stages.find(({ value }) => value === iteration.currentStage)
    console.log('iteration?.currentStage, stages: ', iteration?.currentStage, stages, targetStage)
    setCurrentContent({
      ...targetStage,
      ...comps[iteration.currentStage],
    })
  }, [iteration?.currentStage, stages])

  useEffect(() => {
    console.log('currentContent:', currentContent, iteration?.currentStage, Stages.prepareMining)
  }, [currentContent])

  useEffect(() => {
    if (updated) {
      message.info(t('task.fusion.create.success.msg'))
      clearCache()
      history.replace(`/home/project/${pid}/iterations`)
    }
  }, [updated])

  const next = (result) => {
    if (!currentContent.next) {
      // next iteration
      callback({
        type: 'create',
        data: {
          round: project.round + 1,
        },
      })
    } else {
      // next
      callback({
        type: 'update',
        params: {
          id: iteration.id,
          currentStage: currentContent.next,
        },
      })
    }
  }

  const skip = () => {
    // skip
    callback({
      type: 'skip',
      params: {
        id: iteration.id,
        currentStage: stages.next,
        [currentContent.output]: 0,
      }
    })
  }

  const ok = (result) => {
    // update current stage
    callback({
      type: 'update',
      params: {
        id: iteration.id,
        currentStage: currentContent.value,
        [currentContent.output]: result.id,
      }
    })
  }

  return currentContent && CurrentAction ?
    <CurrentAction
      step={currentContent}
      result={result}
      {...fixedQuery}
      {...(currentContent.query || {})}
      ok={ok}
      next={next}
      skip={skip}
    /> : null
}

export default StepAction
