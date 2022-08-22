import { useEffect, useState } from 'react'
import { Modal } from '@antd'

import t from '@/utils/t'
import { MERGESTRATEGY } from '@/constants/dataset'

const { confirm, error } = Modal

const options = [
  { value: MERGESTRATEGY.HOST, label: 'task.train.duplicated.option.train' },
  { value: MERGESTRATEGY.GUEST, label: 'task.train.duplicated.option.validation' }
]

const useDuplicatedCheck = (onChange = () => { }) => {
  const [checked, setChecked] = useState(false)
  const [duplicated, checkDuplication] = useFetch('dataset/checkDuplication', 0)
  const [trainset, setTrainset] = useState({})
  const [validationset, setValidationset] = useState({})
  const [strategy, setStrategy] = useState(MERGESTRATEGY.NORMAL)

  useEffect(() => {
    if (trainset.id && validationset.id) {
      checkDuplication({ trainSet: trainset.id, validationSet: validationset.id })
      setChecked(true)
    }
  }, [trainset, validationset])

  useEffect(() => {
    if (checked && !duplicated) {
      return ok()
    }
    const allValidation = duplicated === trainset.assetCount
    const allTrain = duplicated === validationset.assetCount
    const allDuplicated = allValidation && allTrain
    if (allDuplicated) {
      return error({
        content: t('task.train.action.duplicated.all'),
        onOk: cancel,
        onCancel: cancel,
      })
    }
    confirm({
      visible: checked,
      content: renderContent(duplicated, allTrain, allValidation),
      onOk: ok,
      onCancel: cancel,
    })
  }, [duplicated, checked])

  const check = (trainDataset, validationDataset) => {
    setTrainset(trainDataset)
    setValidationset(validationDataset)
  }

  function renderContent(duplicated, allTrain, allValidation) {
    const disabled = allValidation ? MERGESTRATEGY.HOST : (allTrain ? MERGESTRATEGY.GUEST : null)
    return <div>
      <span>{t('task.train.duplicated.tip', { duplicated })}</span>
      <Radio.Group
        value={strategy}
        onChange={({ target: { value } }) => setStrategy(value)}
        options={options.map(opt => ({ ...opt, disabled: disabled === opt.value, label: <p>{t(opt.label)}</p> }))}
      />
    </div>
  }

  function ok() {
    onChange(strategy)
  }

  function cancel() {
    setChecked(false)
  }

  return check
}

export default useDuplicatedCheck
