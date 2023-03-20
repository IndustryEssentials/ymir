import { message, MessageArgsProps } from 'antd'
import { getErrorCodeDocLink } from '@/constants/common'
import t from '@/utils/t'

const useErrorMessage = (config: Omit<MessageArgsProps, 'content'> = {}) => {
  return (code: string | number, showLink = true) => {
    const msg = t(`error${code}`)
    const content = (
      <>
        {msg}
        {showLink ? (
          <a href={getErrorCodeDocLink(code)} target="_blank" style={{ display: 'inline-block', paddingLeft: 10 }}>
            {t('common.more')}
          </a>
        ) : null}
      </>
    )
    return message.error(
      {
        ...config,
        content,
      },
      5000,
    )
  }
}

export default useErrorMessage
