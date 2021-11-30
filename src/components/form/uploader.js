import { Button, message, Upload } from "antd"
import ImgCrop from 'antd-img-crop'

import { CloudUploadOutlined } from "@ant-design/icons"
import { getUploadUrl } from "../../services/common"
import storage from '@/utils/storage'
import t from '@/utils/t'
import 'antd/es/slider/style'

const typeFormat = {
  img: ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'],
  zip: ['application/zip'],
  doc: ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/pdf'],
}

function Uploader({ className, value=[], format="zip", label, max = 200, 
  maxCount = 1, info = '', type='', crop = false, showUploadList = true, onChange = ()=> {}}) {

  label = label || t('model.add.form.upload.btn')

  function onFileChange({ file }) {
    if (file.status === 'done') {
      uploadSuccess(file.response)
    }
  }

  function beforeUpload(file) {
    console.log('file: ', file)
    const isValid = typeFormat[format].indexOf(file.type) > -1
    if (!isValid) {
      message.error('You can only upload valid format file!')
    }
    const isOver = file.size / 1024 / 1024 < max
    if (!isOver) {
      message.error(`File must smaller than ${max}MB!`)
    }
    return isValid && isOver ? true : Upload.LIST_IGNORE
  }

  const uploadSuccess = ({ code, result }) => {
    if (code === 0) {
      onChange(result)
    }
  }

  const uploader = <Upload
        className={className}
        fileList={value}
        action={getUploadUrl()}
        name='file'
        headers={{ "Authorization": `Bearer ${storage.get("access_token")}` }}
        accept={format}
        onChange={onFileChange}
        beforeUpload={beforeUpload}
        maxCount={maxCount}
        showUploadList={showUploadList}
      >
        <Button type={type} icon={<CloudUploadOutlined />}>{label}</Button>
      </Upload>

  return (
    <>
      { format === 'img' && crop ? <ImgCrop rotate>{uploader}</ImgCrop> : uploader}
      {info ? <p style={{ margin: '10px 0' }}>{info}</p> : null }
    </>
  )
}

export default Uploader
