import { TASKSTATES, TASKTYPES } from "./task"
import { TYPES } from './image'
import t from "@/utils/t"

export const getTaskTypes = () => [
  { key: "all", value: "", label: t("common.all") },
  { key: "train", value: TASKTYPES.TRAINING, label: t("task.type.train") },
  { key: "mining", value: TASKTYPES.MINING, label: t("task.type.mining") },
  { key: "label", value: TASKTYPES.LABEL, label: t("task.type.label") },
  { key: "fusion", value: TASKTYPES.FUSION, label: t("task.type.fusion") },
]

export const getTaskStates = () => [
  { key: "all", value: "", label: t("common.all") },
  { key: "pending", value: TASKSTATES.PENDING, label: t("task.state.pending"), color: 'default' },
  { key: "doing", value: TASKSTATES.DOING, label: t("task.state.doing"), color: 'rgb(250, 211, 55)' },
  { key: "finish", value: TASKSTATES.FINISH, label: t("task.state.finish"), color: 'rgb(53, 202, 203)' },
  { key: "failure", value: TASKSTATES.FAILURE, label: t("task.state.failure"), color: 'rgb(242, 99, 123)' },
  { key: "terminated", value: TASKSTATES.TERMINATED, label: t("task.state.terminated"), color: 'rgb(242, 99, 123)' },
]

export const getTimes = () => [
  { label: t("common.all"), value: 0 },
  { label: t("task.times.current"), value: 1 },
  { label: t("task.times.3day"), value: 3 },
  { label: t("task.times.week"), value: 7 },
  { label: t("task.times.year"), value: 365 },
]

export const getModelImportTypes = () => [
  { key: "all", value: "", label: t("common.all") },
  { key: "train", value: 1, label: t("model.type.train") },
]

export const getDatasetTypes = () => [
  { key: "all", value: "", label: t("common.all") },
  { key: "mining", value: TASKTYPES.MINING, label: t("dataset.type.mine") },
  { key: "label", value: TASKTYPES.LABEL, label: t("dataset.type.label") },
  { key: "fusion", value: TASKTYPES.FUSION, label: t("dataset.type.fusion") },
  { key: "import", value: TASKTYPES.IMPORT, label: t("dataset.type.import") },
  { key: "empty", value: 105, label: '' },
]

export const getImageTypes = () => [
  { key: "all", value: undefined, label: t("common.all") },
  { key: "train", value: TYPES.TRAINING, label: t("image.type.train") },
  { key: "mining", value: TYPES.MINING, label: t("image.type.mining") },
  { key: "inference", value: TYPES.INFERENCE, label: t("image.type.inference") },
]
