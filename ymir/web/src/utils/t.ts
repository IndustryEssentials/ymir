import { useIntl, getLocale } from "umi"

let intl: any = null
let locale: any = null

const getIntl = () => {
  if (!intl || locale !== getLocale()) {
    intl = useIntl()
    locale = getLocale()
  }
  return intl
}

function _MSG({ id = '', values = {} }) {
  const uIntl = getIntl()
  return uIntl.formatMessage({ id }, values)
}

export const initIntl = (prefix: string = '') => {
  const _helper = (id: string, values = {}, _prefix: string = '') => {
    const key = _prefix ? `${_prefix}.${id}` : (prefix ? `${prefix}.${id}` : id)
    return _MSG({ id: key, values })
  }
  return _helper
}

const showIntl = (id: string, values = {}, prefix: string) => {
  if (!id) {
    return
  }
  try {
    return initIntl(prefix)(id, values)
  } catch (err) {
    console.warn('locale error: ', id, values, err)
  }
}

export default showIntl
