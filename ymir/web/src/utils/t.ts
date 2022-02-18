import { IntlShape } from "react-intl"
import { useIntl } from "umi"

let intl: IntlShape

// not use for string show on initial state
export default (id: string, values = {}) => {
  if (!intl) {
    intl = useIntl()
  }
  try {
    return intl.formatMessage({ id }, values)
  } catch(err) {
    console.log('locale error: ', err)
  }
}

export function formatHtml(id: string, values = {}) {
  if (!intl) {
    intl = useIntl()
  }
  try {
    return intl.formatHTMLMessage({ id }, values)
  } catch(err) {
    console.log('locale error: ', err)
  }
}
