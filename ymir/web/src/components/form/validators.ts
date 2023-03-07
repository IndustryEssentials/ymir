

import t from '@/utils/t'
type ValidatorType<ValueType = string> = (rule: unknown, value?: ValueType) => Promise<string|void>
export const phoneValidate: ValidatorType = (_, value) => {
  const reg = /^\+?\d{5,18}$/
  if (value && !reg.test(value)) {
    return Promise.reject(t("signup.phone.format.msg"))
  }
  return Promise.resolve()
}

export const trimValidator: ValidatorType = (_, value) => {
  if ((value || '').trim().length <= 0) {
    return Promise.reject()
  }
  return Promise.resolve()
}

export const urlValidator: ValidatorType = (_, value) => {
  const reg = /^(([^:/?#]+):)?(\/\/([^\/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?$/
  if(reg.test((value || '').trim())) {
    return Promise.resolve()
  } else {
    return Promise.reject(t('dataset.add.validate.url.invalid'))
  }
}