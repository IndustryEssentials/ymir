import { message } from 'antd'
import { useDispatch } from 'umi'
import t from '@/utils/t'

const useRestore = (pid) => {
  const dispatch = useDispatch()
  const restore = (module, ids) => {
    if (!ids.length) {
      return message.warn(t('common.selected.required'))
    }
    const type = `${module}/restore`
    return dispatch({ type, payload: { pid, ids }, })
  }

  return restore
}

export default useRestore
