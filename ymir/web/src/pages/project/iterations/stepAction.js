import { useEffect, useState } from 'react'
import { useSelector } from 'umi'

import { STEP } from '@/constants/iteration'

import Fusion from '@/components/task/fusion'
import Mining from '@/components/task/mining'
import Label from '@/components/task/label'
import Merge from '@/components/task/merge'
import Training from '@/components/task/training'
import Buttons from './buttons'
import NextIteration from './nextIteration'
import FinishStep from './FinishStep'

const Action = (Comp, props = {}) => <Comp {...props} />

const StepAction = ({ steps, selected, iteration, callback = () => {} }) => {
  const actionPanelExpand = useSelector(({ iteration }) => iteration.actionPanelExpand)
  const [currentStep, setCurrentStep] = useState(null)
  const [selectedStep, setSelectedStep] = useState(null)
  const [CurrentAction, setCurrentAction] = useState(null)
  const result = useSelector((state) => {
    const res = currentStep?.resultType ? state[currentStep.resultType][currentStep.resultType] : {}
    return res[currentStep?.resultId] || {}
  })
  const [state, setState] = useState(-1)

  const comps = {
    [STEP.prepareMining]: {
      comp: Fusion,
      query: (settings = {}) => ({
        did: settings.mining_dataset_id,
        strategy: settings.mining_strategy,
        chunk: settings.sampling_count,
        excludes: settings.exclude_datasets,
      }),
    },
    [STEP.mining]: {
      comp: Mining,
      query: (settings = {}) => ({
        did: settings.dataset_id,
        mid: [settings.model_id, null],
        image: settings.docker_image_id,
        generate_annotations: settings.generate_annotations,
        config: settings.docker_image_config ? JSON.parse(settings.docker_image_config) : undefined,
        topK: settings.top_k,
      }),
    },
    [STEP.labelling]: {
      comp: Label,
      query: (settings = {}) => ({
        did: settings.dataset_id,
        type: settings.annotation_type,
        url: settings.extra_url,
      }),
    },
    [STEP.merging]: {
      comp: Merge,
      query: (settings = {}) => ({
        mid: settings.dataset_id ? [settings.dataset_id] : undefined,
        did: settings.training_dataset_id,
      }),
    },
    [STEP.training]: {
      comp: Training,
      query: (settings = {}) => ({
        did: settings.dataset_id,
        image: settings.docker_image_id,
        config: settings.docker_image_config ? JSON.parse(settings.docker_image_config) : undefined,
        test: settings.validation_dataset_id,
        mid: settings.model_id ? [settings.model_id, settings.model_stage_id] : undefined,
      }),
    },
    [STEP.next]: {
      comp: NextIteration,
    },
  }
  const fixedQuery = {
    iterationId: iteration.id,
    from: 'iteration',
  }

  useEffect(() => {
    if (currentStep) {
      const bottom = <Buttons step={currentStep} state={state} next={next} skip={skip} react={react} />
      const props = {
        bottom,
        step: currentStep,
        hidden: state >= 0,
        query: { ...fixedQuery, ...(currentStep.query || {}), ...(currentStep.preSetting || {}) },
        ok,
      }
      setCurrentAction(Action(currentStep.comp, props))
    }
  }, [currentStep, state])

  useEffect(() => {
    if (currentStep) {
      const state = result?.id ? result.state : currentStep.state
      setState(Number.isInteger(state) ? state : -1)
    }
  }, [result?.state, currentStep?.state])

  useEffect(() => {
    if (!iteration || !steps.length) {
      return
    }
    const name = iteration?.currentStep?.name || STEP.next
    const targetStep = getStep(name, steps)
    const targetComps = comps[name]
    const query = !iteration.end ? targetComps.query(targetStep.preSetting) : {}
    setCurrentStep({
      ...targetStep,
      ...targetComps,
      query,
    })
  }, [steps, iteration])

  useEffect(() => {
    if (!selected) {
      return
    }
    setSelectedStep(getStep(selected, steps))
  }, [steps, selected])

  useEffect(() => {
    if (!selected && currentStep?.resultId) {
      setSelectedStep(currentStep)
    }
  }, [currentStep, selected])

  const react = () => {
    setState(-2)
  }

  const next = () =>
    callback({
      type: 'next',
    })

  const skip = () =>
    callback({
      type: 'skip',
    })

  const ok = (result) => {
    if (currentStep.end) {
      // next iteration
      callback({
        type: 'create',
      })
    } else {
      // update current stage
      callback({
        type: 'bind',
        data: {
          taskId: result.id,
        },
      })
    }
  }

  function getStep(name, steps = []) {
    const step = steps.find(({ value }) => value === (name || STEP.next))
    return step
  }

  function showFinishStep() {
    const isCurrent = !selected || currentStep?.value === selected
    const hasResult = !!selectedStep?.resultId
    return isCurrent ? state >= 0 : hasResult
  }

  return (
    <div hidden={!actionPanelExpand}>
      {showFinishStep() ? <FinishStep step={selectedStep} /> : null}
      {selected && selected !== currentStep?.value ? null : CurrentAction}
    </div>
  )
}

export default StepAction
