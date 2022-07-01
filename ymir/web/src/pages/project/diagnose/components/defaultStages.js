import { useEffect, useState } from "react"
import { Form, Select } from "antd"
import Panel from "@/components/form/panel"
import useFetch from "@/hooks/useFetch"
import t from "@/utils/t"
const DefaultStages = ({ diagnosing, models = [] }) => {
  const [result, setStage] = useFetch('model/setRecommendStage')
  const [uniqueModels, setModels] = useState([])

  useEffect(() => {
    const unique = models.reduce((prev, model) => prev.some(md => md.id === model.id) ? prev : [...prev, model], [])
    setModels(unique)
  }, [models])

  useEffect(() => {
    if (result) {
      uniqueModels.forEach(model => model.id === result.id && (model.recommendStage = result.recommendStage))
    }
  }, [result])


  const clickHandle = (model, stage) => {
    setStage({ model, stage })
  }

  return diagnosing && models.length ?
    <Panel label={t('model.diagnose.stage.label')} toogleVisible={false}>
      {uniqueModels.map(model =>
        <Form.Item label={`${model.name} ${model.versionName}`}>
          <Select defaultValue={model.recommendStage} onChange={(value) => clickHandle(model.id, value)}>
            {model.stages.map(stage => <Select.Option key={stage.id} value={stage.id}>{stage.name}</Select.Option>)}
          </Select>
        </Form.Item>)}
    </Panel> : null
}

export default DefaultStages
