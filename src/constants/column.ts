import { TASKSTATES } from "./task"
import t from "@/utils/t"

export const getSetStates = () => [
  { key: "pending", value: TASKSTATES.PENDING, label: t("dataset.state.importing") },
  { key: "doing", value: TASKSTATES.DOING, label: t("dataset.state.importing") },
  { key: "finish", value: TASKSTATES.FINISH, label: t("dataset.state.imported"), color: 'green' },
  { key: "failure", value: TASKSTATES.FAILURE, label: t("dataset.state.failure"), color: 'red' },
]
