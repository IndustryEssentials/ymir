import { Button, ButtonProps, message, Upload } from 'antd'
import { useState, useEffect, FC } from 'react'
import ImgCrop from 'antd-img-crop'

import { CloudUploadOutlined } from '@ant-design/icons'
import { getUploadUrl } from '@/services/common'
import storage from '@/utils/storage'
import t from '@/utils/t'
import 'antd/es/slider/style'
import { UploadFile } from 'antd/lib/upload/interface'

export type { UploadFile }

type Props = {
  className?: string
  value?: UploadFile[]
  format?: string
  label?: string
  max?: number
  maxCount?: number
  info?: string
  crop?: boolean
  btnProps?: ButtonProps
  showUploadList?: boolean
  onChange?: (files: UploadFile[], url: string) => void
  onRemove?: (file: UploadFile) => void
}

type ResponseType = {
  code: number,
  result: string
}

const fileSuffix: { [type: string]: string[] } = {
  img: ['jpeg', 'jpg', 'png', 'bmp'],
  avatar: ['jpeg', 'jpg', 'png', 'gif', 'bmp'],
  zip: ['zip'],
  doc: ['doc', 'docx', 'txt', 'pdf'],
  all: ['*'],
}

const Uploader: FC<Props> = ({
  className,
  value = null,
  format = 'zip',
  label,
  max = 200,
  maxCount = 1,
  info = '',
  crop = false,
  btnProps = {},
  showUploadList = true,
  onChange = () => {},
  onRemove = () => {},
}) => {
  label = label || t('model.add.form.upload.btn')
  const [files, setFiles] = useState<UploadFile[]>()

  useEffect(() => {
    value && value.length && setFiles(value)
  }, [value])

  function onFileChange({ file, fileList }: { file: UploadFile; fileList: UploadFile[] }) {
    if (file.status === 'done') {
      uploadSuccess(file.response)
    }
    setFiles([...fileList])
  }

  function beforeUpload(file: File) {
    return validFile(file) || Upload.LIST_IGNORE
  }

  function validFile(file: File) {
    const fix = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
    const isValid = format === 'all' ? true : fileSuffix[format].indexOf(fix) > -1
    if (!isValid) {
      message.error(t('common.uploader.format.error'))
    }
    const size = file.size || 0
    const isOver = size / 1024 / 1024 < max
    if (!isOver) {
      message.error(t('common.uploader.size.error', { max }))
    }
    return isValid && isOver
  }

  const beforeCrop = (file: File) => validFile(file)

  const uploadSuccess = ({ code, result }: ResponseType) => code === 0 && files && onChange(files, result)

  const uploader = (
    <Upload
      className={className}
      fileList={files}
      action={getUploadUrl()}
      name="file"
      headers={{ Authorization: `Bearer ${storage.get('access_token')}` }}
      onChange={onFileChange}
      onRemove={onRemove}
      beforeUpload={beforeUpload}
      maxCount={maxCount}
      showUploadList={showUploadList}
    >
      <Button type='primary' ghost icon={<CloudUploadOutlined />} {...btnProps}>
        {label}
      </Button>
    </Upload>
  )

  return (
    <>
      {format === 'avatar' && crop ? (
        <ImgCrop rotate beforeCrop={beforeCrop}>
          {uploader}
        </ImgCrop>
      ) : (
        uploader
      )}
      {info ? <p style={{ margin: '10px 0' }}>{info}</p> : null}
    </>
  )
}

export default Uploader
