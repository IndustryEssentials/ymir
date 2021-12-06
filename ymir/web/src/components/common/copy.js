import { message } from "antd"
import { useRef } from "react"
import styles from "./common.less"

function Copy({ text, label = "Copy" }) {
  const inputRef = useRef()
  const copyText = (e) => {
    e.stopPropagation()
    e.preventDefault()
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
