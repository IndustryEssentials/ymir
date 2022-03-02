import { IntlShape } from "react-intl"
import { useIntl } from "umi"

let intl: IntlShape

// not use for string show on initial state
export default (id: string, values = {}) => {
  try {
    if (!intl) {
      intl = useIntl()
    }
    return intl.formatMessage({ id }, values)
  } catch (err) {
    console.log('locale error: ')
  }
}

export function formatHtml(id: string, values = {}) {
  try {
    if (!intl) {
      intl = useIntl()
    }
    return intl.formatHTMLMessage({ id }, values)
  } catch (err) {
    // console.log('locale error: ', err)
  }
}
