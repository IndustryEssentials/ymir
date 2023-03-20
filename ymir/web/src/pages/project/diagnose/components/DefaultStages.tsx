import { FC, useEffect, useState } from "react"
import { Form, Select } from "antd"
import Panel from "@/components/form/panel"
import useFetch from "@/hooks/useFetch"
import t from "@/utils/t"
import VersionName from '@/components/result/VersionName'

const DefaultStages: FC<{ models: YModels.Model[] }> = ({ models = [] }) => {
  const [result, setStage] = useFetch('model/setRecommendStage')

  useEffect(() => {
    if (result) {
      models.forEach(model => model.id === result.id && (model.recommendStage = result.recommendStage))
    }
  }, [result])


  const clickHandle = (model: number, stage: number) => {
    setStage({ model, stage })
  }

  return models.length ?
    <Panel label={t('model.diagnose.stage.label')} toogleVisible={false}>
      {models.map(model =>
        <Form.Item key={model.id} label={<VersionName result={model} />}>
          <Select defaultValue={model.recommendStage} onChange={(value) => clickHandle(model.id, value)}>
            {model.stages?.map(stage => <Select.Option key={stage.id} value={stage.id}>{stage.name}</Select.Option>)}
          </Select>
        </Form.Item>)}
    </Panel> : null
}

export default DefaultStages
