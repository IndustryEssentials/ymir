import { FC, useEffect } from 'react'
import { notification } from 'antd'
import { useSelector } from 'umi'
import { readyState } from '@/constants/common'
import { isAdmin } from '@/constants/user'
import useRequest from '@/hooks/useRequest'
import t from '@/utils/t'

const key = 'officialImage'

const OfficialImageTip: FC = () => {
  const { official, role } = useSelector(({ image, user }) => ({ official: image.official, role: user.role }))
  const { run: getOfficialImage } = useRequest('image/getOfficialImage')

  useEffect(() => getOfficialImage(), [])

  useEffect(() => {
    if (official && readyState(official.state) && isAdmin(role)) {
      notification.warning({
        key,
        message: t('image.official.tip.title'),
        description: t('image.official.tip'),
        duration: 0,
      })
    } else {
      notification.close(key)
    }
  }, [official, role])
  return <></>
}

export default OfficialImageTip
