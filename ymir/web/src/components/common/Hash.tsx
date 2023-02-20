import { FC } from "react"
import Copy from "./Copy"
import styles from "./common.less"

type Props = {
  value: string,
  width?: number
}

const Hash: FC<Props> = ({ value, width = 160 }) => {
  return (
    <>
      <span className={styles.hash} style={{ maxWidth: width }} title={value}>
        {value}
      </span>
      <Copy text={value} />
    </>
  )
}

export default Hash
