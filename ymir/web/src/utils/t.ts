import { useIntl } from 'umi'

type KeyType = string | number | undefined

function _MSG(id: KeyType = '', values = {}) {
  const uIntl = useIntl()
  return uIntl.formatMessage({ id }, values)
}

export const initIntl = (prefix: string = '') => {
  const _helper = (id: KeyType, values = {}, _prefix: string = '') => {
    const key = _prefix ? `${_prefix}.${id}` : prefix ? `${prefix}.${id}` : id
    return _MSG(key, values)
  }
  return _helper
}

const showIntl = (id: KeyType = '', values = {}, prefix: string = '') => {
  if (id) {
    try {
      return initIntl(prefix)(id, values)
    } catch (err) {
      console.warn('locale error: ', id, values, err)
    }
  }
  return ''
}

export default showIntl
