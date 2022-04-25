import { TASKSTATES, TASKTYPES } from "./task"
import { TYPES } from './image'

export const getImageTypes = () => [
  { key: "all", value: undefined, label: "common.all" },
  { key: "train", value: TYPES.TRAINING, label: "image.type.train" },
  { key: "mining", value: TYPES.MINING, label: "image.type.mining" },
  { key: "inference", value: TYPES.INFERENCE, label: "image.type.inference" },
]
