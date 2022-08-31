import { useCallback, useEffect, useState } from 'react'
import { Modal, Radio } from 'antd'

import t from '@/utils/t'
import { MERGESTRATEGY } from '@/constants/dataset'
import useFetch from '@/hooks/useFetch'

const { confirm, error } = Modal

const options = [
  { value: MERGESTRATEGY.HOST, label: 'task.train.duplicated.option.train' },
  { value: MERGESTRATEGY.GUEST, label: 'task.train.duplicated.option.validation' }
]

const ContentRender = ({ duplicated, strategy, disabled, onChange = () => { } }) => {
  const [s, setS] = useState(strategy)
  useEffect(() => onChange(s), [s])
  return <div>
    <span>{t('task.train.duplicated.tip', { duplicated })}</span>
    <Radio.Group
      value={s}
      onChange={({ target: { value } }) => { setS(value) }}
      options={options.map(opt => ({
        ...opt,
        disabled: disabled === opt.value,
        label: <p>{t(opt.label)}</p>
      }))}
    />
  </div>
}

const useDuplicatedCheck = (onChange = () => { }) => {
  const [_, checkDuplication] = useFetch('dataset/checkDuplication', 0)
  let strategy = MERGESTRATEGY.NORMAL

  const ok = () => {
    onChange(strategy)
  }

  const check = async (trainDataset, validationDataset) => {
    const result = await checkDuplication({ trainSet: trainDataset?.id, validationSet: validationDataset?.id })
    if (typeof result !== 'undefined') {
      checkHandle(result, trainDataset, validationDataset)
    }
  }

  const checkHandle = (duplicated, trainDataset, validationDataset) => {
    if (!duplicated) {
      return ok()
    }
    const allValidation = duplicated === trainDataset.assetCount
    const allTrain = duplicated === validationDataset.assetCount
    const allDuplicated = allValidation && allTrain
    if (allDuplicated) {
      return error({
        content: t('task.train.action.duplicated.all'),
      })
    }
    PopConfirm(duplicated, allValidation, allTrain)
  }

  const PopConfirm = (duplicated, allValidation, allTrain) => {

    const disabled = allValidation ? MERGESTRATEGY.GUEST : (allTrain ? MERGESTRATEGY.HOST : null)
    const value = allValidation ? MERGESTRATEGY.HOST : (allTrain ? MERGESTRATEGY.GUEST : strategy)
    strategy = value
    confirm({
      visible: true,
      content: <ContentRender duplicated={duplicated} disabled={disabled} strategy={value} onChange={value => (strategy = value)} />,
      onOk: ok,
      destroyOnClose: true,
    })
  }

  return check
}

export default useDuplicatedCheck
