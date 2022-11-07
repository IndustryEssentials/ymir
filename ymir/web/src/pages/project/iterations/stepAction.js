import { useEffect, useState } from "react"
import { useSelector } from "umi"

import { STEP } from "@/constants/iteration"

import Fusion from "@/components/task/fusion"
import Mining from "@/components/task/mining"
import Label from "@/components/task/label"
import Merge from "@/components/task/merge"
import Training from "@/components/task/training"
import Buttons from "./buttons"
import NextIteration from "./nextIteration"

const Action = (Comp, props = {}) => <Comp {...props} />

const StepAction = ({ steps, iteration, callback = () => {} }) => {
  const actionPanelExpand = useSelector(
    ({ iteration }) => iteration.actionPanelExpand
  )
  const [currentContent, setCurrentContent] = useState(null)
  const [CurrentAction, setCurrentAction] = useState(null)
  const result = useSelector((state) => {
    const res = currentContent?.resultType
      ? state[currentContent.resultType][currentContent.resultType]
      : {}
    return res[currentContent?.resultId] || {}
  })
  const [state, setState] = useState(-1)

  const comps = {
    [STEP.prepareMining]: {
      comp: Fusion,
      query: (settings = {}) => ({
        did: settings.mining_dataset_id,
        strategy: settings.mining_strategy,
        chunk: settings.chunk_size,
      }),
    },
    [STEP.mining]: {
      comp: Mining,
      query: (settings = {}) => ({
        did: settings.dataset_id,
        mid: [settings.model_id, null],
        topK: settings.top_k,
      }),
    },
    [STEP.labelling]: {
      comp: Label,
      query: (settings = {}) => ({
        did: settings.dataset_id,
      }),
    },
    [STEP.merging]: {
      comp: Merge,
      query: (settings = {}) => ({
        did: settings.training_dataset_id,
        mid: settings.dataset_id ? [settings.dataset_id] : undefined,
      }),
    },
    [STEP.training]: {
      comp: Training,
      query: (settings = {}) => ({
        did: settings.dataset_id,
        test: settings.validation_dataset_id,
      }),
    },
    [STEP.next]: {
      comp: NextIteration,
    },
  }
  const fixedQuery = {
    iterationId: iteration.id,
    from: "iteration",
  }

  useEffect(() => {
    if (currentContent) {
      const bottom = (
        <Buttons
          step={currentContent}
          state={state}
          next={next}
          skip={skip}
          react={react}
        />
      )
      const props = {
        bottom,
        step: currentContent,
        hidden: state >= 0,
        query: { ...fixedQuery, ...(currentContent.query || {}) },
        ok,
      }
      console.log("currentContent:", currentContent, props)
      setCurrentAction(Action(currentContent.comp, props))
    }
  }, [currentContent, state])

  useEffect(() => {
    if (currentContent) {
      const state = result?.id ? result.state : currentContent.state
      setState(Number.isInteger(state) ? state : -1)
    }
  }, [result?.state, currentContent?.state])

  useEffect(() => {
    if (!iteration || !steps.length) {
      return
    }
    const targetStep = steps.find(
      ({ value }) => value === (iteration?.currentStep?.name || STEP.next)
    )
    console.log("iteration:", iteration, targetStep)
    if (!iteration.end) {
      const targetComps = comps[iteration.currentStep.name]
      const query = targetComps.query(targetStep.preSetting)
      setCurrentContent({
        ...targetStep,
        ...targetComps,
        query,
      })
    } else {
      setCurrentContent({
        ...comps[STEP.next],
        ...targetStep,
        current: STEP.next,
      })
    }
  }, [steps, iteration])

  const react = () => {
    setState(-2)
  }

  const next = () =>
    callback({
      type: "next",
    })

  const skip = () =>
    callback({
      type: "skip",
    })

  const ok = (result) => {
    if (!currentContent.next) {
      // next iteration
      callback({
        type: "create",
      })
    } else {
      // update current stage
      callback({
        type: "bind",
        data: {
          taskId: result.id,
        },
      })
    }
  }

  return <div hidden={!actionPanelExpand}>{CurrentAction}</div>
}

export default StepAction
