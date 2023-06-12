import { useState, useEffect, useRef, FC } from 'react'
import { Input, InputRef } from 'antd'
type Props = {
  value: string
  onChange: (value: string) => void
  validate: (value: string) => boolean | void
  dup?: boolean
}

const EditCell: FC<Props> = ({ value, onChange, validate, dup }) => {
  const [name, setName] = useState<string>()
  const [editing, setEditing] = useState(false)
  const inputRef = useRef<InputRef>(null)

  useEffect(() => setName(value), [value])
  useEffect(() => {
    if (editing) {
      inputRef.current?.focus()
    }
  }, [editing])

  return (
    <div style={{ border: dup ? '1px solid red' : 'none' }}>
      {editing ? (
        <Input
          ref={inputRef}
          value={name}
          onChange={({ target }) => setName(target.value)}
          onBlur={({ target }) => {
            const value = target.value
            if (validate(value)) {
              onChange(value)
            }
            setEditing(false)
          }}
        />
      ) : (
        <div onMouseEnter={() => setEditing(true)} style={{ cursor: 'pointer' }}>
          {value}
        </div>
      )}
    </div>
  )
}

export default EditCell
