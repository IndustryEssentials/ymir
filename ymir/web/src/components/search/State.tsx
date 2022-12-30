import { ResultStates, statesLabel } from '@/constants/common'
import { Select, SelectProps } from 'antd'
import { FC } from 'react'

import t from '@/utils/t'

type Props = SelectProps<ResultStates>
const states = [ResultStates.VALID, ResultStates.READY, ResultStates.INVALID]
const defaultAll = { label: t('common.all'), value: -1 }

const State: FC<Props> = (props) => {
  const options = [
    defaultAll,
    ...states.map((state) => ({
      value: state,
      label: t(statesLabel(state)),
    })),
  ]
  return <Select defaultValue={-1} {...props} options={options} style={{ width: 200 }}></Select>
}

export default State
