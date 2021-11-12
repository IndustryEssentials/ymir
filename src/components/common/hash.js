import Copy from "./copy"
import styles from "./common.less"

function Hash({ value, width }) {
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
