import { Button, message, Upload } from "antd"
import { useState, useEffect } from 'react'
import ImgCrop from 'antd-img-crop'

import { CloudUploadOutlined } from "@ant-design/icons"
import { getUploadUrl } from "../../services/common"
import storage from '@/utils/storage'
import t from '@/utils/t'
import 'antd/es/slider/style'

const fileSuffix = {
  img: ['jpeg', 'jpg', 'png', 'bmp'],
  avatar: ['jpeg', 'jpg', 'png', 'gif', 'bmp'],
  zip: ['zip'],
  doc: ['doc', 'docx', 'txt', 'pdf'],
  all: ['*'],
}

function Uploader({ className, value=null, format="zip", label, max = 200, 
  maxCount = 1, info = '', type='', crop = false, showUploadList = true, onChange = ()=> {}, onRemove = () => {}}) {

  label = label || t('model.add.form.upload.btn')
  const [files, setFiles] = useState(null)

  useEffect(() => {
    value && value.length && setFiles(value)
  }, [value])

  function onFileChange({ file, fileList }) {
    if (file.status === 'done') {
      uploadSuccess(file.response)
    }
    setFiles([...fileList])
  }

  function beforeUpload(file) {
    return validFile(file) || Upload.LIST_IGNORE
  }

  function validFile(file) {
    const fix = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
    const isValid = format === 'all' ? true : fileSuffix[format].indexOf(fix) > -1
    if (!isValid) {
      message.error(t('common.uploader.format.error'))
    }
    const isOver = file.size / 1024 / 1024 < max
    if (!isOver) {
      message.error(t('common.uploader.size.error', { max }))
    }
    return isValid && isOver
  }

  function beforeCrop(file) {
    return validFile(file)
  }

  const uploadSuccess = ({ code, result }) => {
    if (code === 0) {
      onChange(files, result)
    }
  }

  const uploader = <Upload
        className={className}
        fileList={files}
        action={getUploadUrl()}
        name='file'
        headers={{ "Authorization": `Bearer ${storage.get("access_token")}` }}
        // accept={fileSuffix[format].join(',')}
        onChange={onFileChange}
        onRemove={onRemove}
        beforeUpload={beforeUpload}
        maxCount={maxCount}
        showUploadList={showUploadList}
      >
        <Button type={type} icon={<CloudUploadOutlined />}>{label}</Button>
      </Upload>

  return (
    <>
      { format === 'avatar' && crop ? <ImgCrop rotate beforeCrop={beforeCrop}>{uploader}</ImgCrop> : uploader}
      {info ? <p style={{ margin: '10px 0' }}>{info}</p> : null }
    </>
  )
}

export default Uploader
