import { ResultStates, statesLabel } from '@/constants/common'
import { Select, SelectProps } from 'antd'
import { FC } from 'react'

import t from '@/utils/t'

type Props = SelectProps<ResultStates>
const states = [ResultStates.VALID, ResultStates.READY, ResultStates.INVALID]

const State: FC<Props> = (props) => {
  const options = states.map((state) => ({
    value: state,
    label: t(statesLabel(state)),
  }))
  return <Select {...props} options={options} placeholder={t('common.state')} allowClear style={{ width: 200 }}></Select>
}

export default State
