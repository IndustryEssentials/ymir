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

const StepAction = ({
  steps,
  iteration,
  project,
  prevIteration,
  callback = () => {},
}) => {
  const actionPanelExpand = useSelector(
    ({ iteration }) => iteration.actionPanelExpand
  )
  const [currentContent, setCurrentContent] = useState(null)
  const [CurrentAction, setCurrentAction] = useState(null)
  const result = useSelector(({ dataset, model }) => {
    const isModel = currentContent?.value === STEP.training
    const res = isModel ? model.model : dataset.dataset
    return res[currentContent?.result] || {}
  })
  const [state, setState] = useState(-1)

  const comps = {
    [STEP.prepareMining]: {
      comp: Fusion,
      query: {
        did: project.miningSet?.id,
        strategy: project.miningStrategy,
        chunk: project.chunkSize || undefined,
      },
    },
    [STEP.mining]: {
      comp: Mining,
      query: {
        did: iteration.miningSet,
        mid: prevIteration.id
          ? [prevIteration.model, null]
          : project.modelStage,
      },
    },
    [STEP.labelling]: {
      comp: Label,
      query: {
        did: iteration.miningResult,
      },
    },
    [STEP.merging]: {
      comp: Merge,
      query: {
        did: prevIteration.trainUpdateSet || project.trainSetVersion,
        mid: iteration.labelSet ? [iteration.labelSet] : undefined,
      },
    },
    [STEP.training]: {
      comp: Training,
      query: {
        did: iteration.trainUpdateSet,
        test: iteration.testSet,
      },
    },
    [STEP.next]: {
      comp: NextIteration,
      query: {},
    },
  }
  const fixedQuery = {
    iterationId: iteration.id,
    currentStep: iteration.currentStep.name,
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
        query: { ...fixedQuery, ...currentContent.query },
        ok,
      }
      console.log("props:", props)
      setCurrentAction(Action(currentContent.comp, props))
    }
    console.log("currentContent:", currentContent, state)
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
      ({ value }) => value === iteration.currentStep.name
    )
    setCurrentContent({
      ...targetStep,
      ...comps[iteration.currentStep.name],
    })
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
