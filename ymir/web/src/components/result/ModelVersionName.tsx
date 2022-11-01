import React from "react"
import { getRecommendStage, getStage } from "@/constants/model"
import { ModelVersion } from "@/interface/model"
import VersionName from "./VersionName"

type Props = { result: ModelVersion, stageId?: number }
const ModelVersionName: React.FC<Props> = ({ result, stageId }) => {
    const stage = stageId ? getStage(result, stageId) : getRecommendStage(result)
    const extra = stage?.name
    return <VersionName result={result} extra={extra} />
}

export default ModelVersionName
