import { FC, useState, useEffect } from 'react'
import { useSelector } from 'umi'
import t from '@/utils/t'
import useRequest from './useRequest'
import { Image } from '@/constants'
import { isAdmin } from '@/constants/user'
import { message, Modal } from 'antd'
import { readyState } from '@/constants/common'

const useGroundedSAMValidator = () => {
  const { role } = useSelector((state) => state.user.user)
  const { runAsync: getGroundedSAMImage } = useRequest<Image>('image/getGroundedSAMImage', {
    loading: false,
  })
  const { runAsync: createGroundedSAMImage } = useRequest('image/createGroundedSAMImage')

  useEffect(() => {}, [])

  const validate = () => {
    return new Promise(async (resolve, reject) => {
      const gsImage = await getGroundedSAMImage()
      if (!gsImage) {
        if (!isAdmin(role)) {
          Modal.info({
            title: 'Grounded-SAM Image',
            content: t('llmm.groundedsam.image.add.user.invalid'),
          })
          return reject(t('llmm.groundedsam.image.add.user.invalid'))
        }
        Modal.confirm({
          title: 'Grounded-SAM Image',
          content: <>{t('llmm.groundedsam.image.add.tip')}</>,
          onOk: async () => {
            const result = await createGroundedSAMImage()
            if (result) {
              message.success(t('llmm.groundedsam.image.add.success'))
              resolve(false)
            }
          },
        })
        return
      } else {
        if (readyState(gsImage.state)) {
          Modal.info({ content: t('llmm.groundedsam.image.add.success') })
          reject()
        }
      }
      resolve(true)
    })
  }
  return validate
}

export default useGroundedSAMValidator
