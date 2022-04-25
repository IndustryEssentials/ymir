import { TASKSTATES } from "./task"

export const getSetStates = () => [
  { key: "pending", value: TASKSTATES.PENDING, label: "dataset.state.ready" },
  { key: "doing", value: TASKSTATES.DOING, label: "dataset.state.ready" },
  { key: "finish", value: TASKSTATES.FINISH, label: "dataset.state.valid", color: 'green' },
  { key: "failure", value: TASKSTATES.FAILURE, label: "dataset.state.invalid", color: 'red' },
]
