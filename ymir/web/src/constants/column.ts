import { TASKSTATES } from "./task"
import t from "@/utils/t"

export const getSetStates = () => [
  { key: "pending", value: TASKSTATES.PENDING, label: t("dataset.state.ready") },
  { key: "doing", value: TASKSTATES.DOING, label: t("dataset.state.ready") },
  { key: "finish", value: TASKSTATES.FINISH, label: t("dataset.state.valid"), color: 'green' },
  { key: "failure", value: TASKSTATES.FAILURE, label: t("dataset.state.invalid"), color: 'red' },
]
