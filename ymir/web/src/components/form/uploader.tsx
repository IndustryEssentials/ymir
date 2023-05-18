import { Button, ButtonProps, message, Upload } from 'antd'
import { useState, useEffect, FC } from 'react'
import ImgCrop from 'antd-img-crop'

import { CloudUploadOutlined } from '@ant-design/icons'
import { getUploadUrl } from '@/services/common'
import storage from '@/utils/storage'
import t from '@/utils/t'
import 'antd/es/slider/style'
import { UploadProps, UploadFile } from 'antd/es/upload/interface'
type UFile = UploadFile<ResponseType>
export type { UploadFile, UFile }

type Props = Omit<UploadProps, 'fileList'> & {
  value?: UFile[]
  format?: string
  label?: string
  max?: number
  info?: string
  crop?: boolean
  btnProps?: ButtonProps
}

type ResponseType = {
  code: number
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
  value,
  format = 'zip',
  label,
  max = 200,
  maxCount = 1,
  info = '',
  crop = false,
  btnProps = {},
  onChange = () => {},
  ...rest
}) => {
  label = label || t('model.add.form.upload.btn')
  const [files, setFiles] = useState<UFile[]>()

  useEffect(() => {
    value?.length && setFiles(value)
  }, [value])

  function onFileChange({ file, fileList }: { file: UFile; fileList: UFile[] }) {
    const fileListWithUrl = fileList.map((file) => ({
      ...file,
      url: file?.response?.result,
    }))
    setFiles(fileListWithUrl)

    file.response?.result && onChange({ file, fileList: fileListWithUrl })
  }

  function beforeUpload(file: UFile) {
    return validFile(file) || Upload.LIST_IGNORE
  }

  function validFile(file: UFile | File) {
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

  // const uploadSuccess = (files: UploadFile[], { code, result }: ResponseType) => code === 0 && files && onChange(files, result)

  const uploader = (
    <Upload
      {...rest}
      fileList={files}
      action={getUploadUrl()}
      name="file"
      headers={{ Authorization: `Bearer ${storage.get('access_token')}` }}
      onChange={onFileChange}
      beforeUpload={beforeUpload}
      multiple={maxCount > 1}
    >
      <Button type="primary" ghost icon={<CloudUploadOutlined />} {...btnProps}>
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
