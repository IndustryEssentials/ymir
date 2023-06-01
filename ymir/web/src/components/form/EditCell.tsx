import { useState, useEffect, useRef, FC } from 'react'
import { Input, InputRef } from 'antd'
type Props = {
  value: string
  onChange: (value: string) => void
  validate: (value: string) => boolean | void
}

const EditCell: FC<Props> = ({ value, onChange, validate }) => {
  const [name, setName] = useState<string>()
  const [editing, setEditing] = useState(false)
  const inputRef = useRef<InputRef>(null)

  useEffect(() => setName(value), [value])
  useEffect(() => {
    if (editing) {
      inputRef.current?.focus()
    }
  }, [editing])

  return editing ? (
    <Input
      ref={inputRef}
      value={name}
      onBlur={() => setEditing(false)}
      onChange={({ target }) => {
        const value = target.value
        console.log('value:', value, validate(value))
        if (validate(value)) {
          onChange(value)
        }
        // setEditing(false)
      }}
    />
  ) : (
    <div onMouseEnter={() => setEditing(true)} style={{ cursor: 'pointer' }}>
      {value}
    </div>
  )
}

export default EditCell
