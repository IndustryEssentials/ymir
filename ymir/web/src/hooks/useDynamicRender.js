import { useCallback, useState } from "react"

const useDynamicRender = (field = 'ap') => {
  const [selected, setSelected] = useState(null)

  const render = useCallback((metrics = {}) => {
    const everage = metrics.ci_averaged_evaluation || {}
    const kwMetrics = metrics.ci_evaluations || {}
    const result = (selected === '' ? everage : kwMetrics[selected]) || {}
    const metric = result[field]
    return typeof metric === 'undefined' || metric === -1 ? '-' : metric
  }, [selected, field])

  return [render, setSelected]
}

export default useDynamicRender
