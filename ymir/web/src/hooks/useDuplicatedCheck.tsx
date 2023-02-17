import { FC, useEffect, useState } from 'react'
import { Modal, Radio } from 'antd'

import t from '@/utils/t'
import { MERGESTRATEGYFORTRAIN } from '@/constants/dataset'
import useFetch from '@/hooks/useFetch'

type ContentProps = {
  duplicated: number
  strategy?: MERGESTRATEGYFORTRAIN
  disabled?: MERGESTRATEGYFORTRAIN
  onChange?: (s: MERGESTRATEGYFORTRAIN) => void
}

const { confirm, error } = Modal

const options = [
  { value: MERGESTRATEGYFORTRAIN.ASTRAIN, label: 'task.train.duplicated.option.train' },
  { value: MERGESTRATEGYFORTRAIN.ASVALIDATION, label: 'task.train.duplicated.option.validation' },
]

const ContentRender: FC<ContentProps> = ({ duplicated, strategy, disabled, onChange = () => {} }) => {
  const [s, setS] = useState(strategy)
  useEffect(() => {
    s && onChange(s)
  }, [s])
  return (
    <div>
      <span>{t('task.train.duplicated.tip', { duplicated })}</span>
      <Radio.Group
        value={s}
        onChange={({ target: { value } }) => {
          setS(value)
        }}
        options={options.map((opt) => ({
          ...opt,
          disabled: disabled === opt.value,
          label: <p>{t(opt.label)}</p>,
        }))}
      />
    </div>
  )
}

const useDuplicatedCheck = (onChange: (s: MERGESTRATEGYFORTRAIN) => void = () => {}): ((t: YModels.Dataset, v: YModels.Dataset) => void) => {
  const [_, checkDuplication] = useFetch('dataset/checkDuplication', 0)
  let strategy = MERGESTRATEGYFORTRAIN.STOP

  const ok = () => {
    onChange(strategy)
  }

  const check = async (trainDataset: YModels.Dataset, validationDataset: YModels.Dataset) => {
    const result = await checkDuplication({ trainSet: trainDataset?.id, validationSet: validationDataset?.id })
    if (typeof result !== 'undefined') {
      checkHandle(result, trainDataset, validationDataset)
    }
  }

  const checkHandle = (duplicated: number, trainDataset: YModels.Dataset, validationDataset: YModels.Dataset) => {
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

  const PopConfirm = (duplicated: number, allValidation: boolean, allTrain: boolean) => {
    const disabled = allValidation ? MERGESTRATEGYFORTRAIN.ASVALIDATION : allTrain ? MERGESTRATEGYFORTRAIN.ASTRAIN : undefined
    const value = allTrain ? MERGESTRATEGYFORTRAIN.ASVALIDATION : MERGESTRATEGYFORTRAIN.ASTRAIN
    strategy = value
    confirm({
      visible: true,
      content: <ContentRender duplicated={duplicated} disabled={disabled} strategy={value} onChange={(value) => (strategy = value)} />,
      onOk: ok,
    })
  }

  return check
}

export default useDuplicatedCheck
