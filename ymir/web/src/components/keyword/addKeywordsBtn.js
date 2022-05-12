import { useCallback } from 'react'
import { Button, message } from 'antd'
import useAddKeywords from "@/hooks/useAddKeywords"

import t from '@/utils/t'

const AddKeywordsBtn = ({ keywords, callback = () => {}, ...props }) => {
  const [{ repeated }, add] = useAddKeywords()

  const addNewKeywords = useCallback(async (kws) => {
    const result = await add(kws)
    if (result) {
      if (result.failed && !result.failed.length) {
        message.success(t('keyword.add.success'))
      } else {
        message.error(t('keyword.name.repeat'))
      }
    } else {
      message.error(t('keyword.add.failure'))
    }
    callback(result)
  })

  return <Button {...props} onClick={() => addNewKeywords(keywords)}>{t('dataset.add.label_strategy.add')}</Button>
}

export default AddKeywordsBtn
