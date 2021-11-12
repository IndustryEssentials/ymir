import {
  EditOutlined,
} from '@ant-design/icons'
import { Form, Input } from 'antd'
import { useEffect, useRef, useState } from 'react'
import styles from './editCell.less'

const { Item, useForm } = Form

const EditableCell = ({
  value,
  record,
  dataIndex,
  handleSave,
  editingState = false,
}) => {
  const [editing, setEditing] = useState(false)
  const inputRef = useRef(null)
  const [editForm] = useForm()

  useEffect(() => {
    if (editing) {
      inputRef.current.focus()
    }
  }, [editing])

  const toggleEdit = () => {
    setEditing(!editing)
    editForm.setFieldsValue({
      [dataIndex]: record[dataIndex],
    })
  }

  const save = async () => {
    try {
      const values = await editForm.validateFields()
      toggleEdit()
      handleSave(record, values[dataIndex])
    } catch (errInfo) {
      console.log("Save failed:", errInfo)
    }
  }

  const content = editing ? (
    <Form form={editForm}>
      <Item
        style={{
          margin: 0,
        }}
        name={dataIndex}
        rules={[
          {
            required: true,
            message: `${dataIndex} is required.`,
          },
        ]}
      >
        <Input ref={inputRef} onPressEnter={save} onBlur={save} />
      </Item>
    </Form>
  ) : (
    <div
      style={{
        paddingRight: 24,
        whiteSpace: 'nowrap',
      }}
      onClick={toggleEdit}
    >
      {value}
      <EditOutlined
        className={'edit'}
      />
    </div>
  )
  return (
    <div className={styles.editable_cell}>
      {content}
    </div>
  )
}

export default EditableCell
