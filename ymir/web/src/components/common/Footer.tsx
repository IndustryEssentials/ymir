import { FC } from 'react'
import config from '@/../package.json'

const Footer: FC = () => (
  <footer style={{ textAlign: "center" }}>
    &copy;copyright {config.displayName}@Team 2023 version: { config.version }
  </footer>
)

export default Footer
