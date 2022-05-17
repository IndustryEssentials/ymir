

import t from '@/utils/t'

export const phoneValidate = (rule, value) => {
  const reg = /^\+?\d{5,18}$/
  if (value && !reg.test(value)) {
    return Promise.reject(t("signup.phone.format.msg"))
  }
  return Promise.resolve()
}

export const trimValidator = (_, value) => {
  if (value.trim().length <= 0) {
    return Promise.reject()
  }
  return Promise.resolve()
}

export function urlValidator(_, value) {
  const reg = /^https?:\/\/([\w\-]+(\.[\w\-\:]+)*\/)*[\w\-]+(\.[\w\-]+)*\/?(\?([\w\-\.,@?^=%&:\/~\+#]*)+)?$/
  if(reg.test((value || '').trim())) {
    return Promise.resolve()
  } else {
    return Promise.reject(t('dataset.add.validate.url.invalid'))
  }
}