import { useEffect, useState } from 'react'
import { useSelector } from 'umi'
import { Space } from 'antd'

import { Stages, StageList } from '@/constants/iteration'
import useFetch from '@/hooks/useFetch'

import Fusion from "@/components/task/fusion"
import Mining from "@/components/task/mining"
import Label from "@/components/task/label"
import Merge from "@/components/task/merge"
import Training from "@/components/task/training"
import IterationStepButtons from './buttons'
import Buttons from './buttons'
import NextIteration from './nextIteration'

const Action = (Comp, props = {}) => <Comp {...props} />

const StepAction = ({ stages, iteration, project, prevIteration, callback = () => {} }) => {
  const [updated, updateIteration] = useFetch('iteration/updateIteration')
  const [currentContent, setCurrentContent] = useState(null)
  const [CurrentAction, setCurrentAction] = useState(null)
  const result = useSelector(({ dataset, model }) => {
    const isModel = currentContent?.value === Stages.training
    const res = isModel ? model.model : dataset.dataset
    return res[currentContent?.result] || {}
  })
  const [state, setState] = useState(-1)

  const comps = {
    [Stages.prepareMining]: {
      comp: Fusion, query: {
        did: project.miningSet?.id,
        strategy: project.miningStrategy,
        chunk: project.chunkSize || undefined,
      },
    },
    [Stages.mining]: {
      comp: Mining, query: {
        did: iteration.miningSet,
        mid: prevIteration.id ? [prevIteration.model, null] : project.modelStage,
      },
    },
    [Stages.labelling]: {
      comp: Label, query: {
        did: iteration.miningResult,
      },
    },
    [Stages.merging]: {
      comp: Merge, query: {
        did: prevIteration.trainUpdateSet || project.trainSetVersion,
        mid: iteration.labelSet,
      },
    },
    [Stages.training]: {
      comp: Training, query: {
        did: iteration.trainUpdateSet,
        test: iteration.testSet,
      },
    },
    [Stages.next]: {
      comp: NextIteration, query: {}
    },
  }
  const fixedQuery = {
    iterationId: iteration.id,
    currentStage: iteration.currentStage,
    from: 'iteration'
  }

  useEffect(() => {
    if (currentContent) {
      const bottom = <Buttons step={currentContent} state={state} next={next} skip={skip} react={react} />
      const props = {
        bottom,
        step: currentContent,
        hidden: state >= 0,
        query: { ...fixedQuery, ...currentContent.query },
        ok,
      }
      setCurrentAction(Action(currentContent.comp, props))
    }
  }, [currentContent, state])

  useEffect(() => {
    if (currentContent) {
      const state = result?.id ? result.state : currentContent.state
      setState(state)
    }
  }, [result?.state, currentContent?.state])

  useEffect(() => {
    if (!stages.length) {
      return
    }
    const targetStage = stages.find(({ value }) => value === iteration.currentStage)
    setCurrentContent({
      ...targetStage,
      ...comps[iteration.currentStage],
    })
  }, [iteration?.currentStage, stages])

  useEffect(() => {
    if (updated) {
      message.info(t('task.fusion.create.success.msg'))
      clearCache()
      history.replace(`/home/project/${pid}/iterations`)
    }
  }, [updated])

  const react = () => {
    setState(-2)
  }

  const next = () => {
    // next
    callback({
      type: 'update',
      data: {
        currentStage: currentContent.next.value,
      },
    })
  }

  const skip = () => {
    // skip
    callback({
      type: 'skip',
      data: currentContent.next,
    })
  }

  const ok = (result) => {
    if (!currentContent.next) {
      // next iteration
      callback({
        type: 'create',
      })
    } else {
      // update current stage
      callback({
        type: 'update',
        data: {
          currentStage: currentContent.value,
          [currentContent.output]: result.id,
        }
      })
    }
  }

  return CurrentAction
}

export default StepAction
