import React, { useEffect } from "react"

type Props = {
  step: YModels.PageStep
}
const FinishStep: React.FC<Props> = ({ step }) => {
  const selected = step.selected

  useEffect(() => {
    console.log("step:", step)
  }, [step])
  return selected ? <>hello, {selected}</> : null
}

export default FinishStep
