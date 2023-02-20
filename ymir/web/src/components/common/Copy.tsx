import { FC, MouseEventHandler, useRef } from "react"
import { message } from "antd"
import styles from "./common.less"

type Props = {
  text: string,
  label?: string
}
const Copy: FC<Props> = ({ text, label = "Copy" }) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const copyText: MouseEventHandler<HTMLSpanElement> = (e) => {
    e.stopPropagation()
    e.preventDefault()
    if (!inputRef.current) {
      return
    }
    inputRef.current.select()
    document.execCommand("copy")
    message.info(`${text} Copied!`)
  }
  return (
    <>
      <span className={styles.copy} onClick={copyText}>
        {label}
      </span>
      <input
        ref={inputRef}
        type="text"
        readOnly
        className={styles.hiddenInput}
        value={text || ""}
      />
    </>
  )
}

export default Copy
