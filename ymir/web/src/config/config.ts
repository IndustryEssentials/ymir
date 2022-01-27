import { defineConfig } from "umi"
import locale from "./locale"
import routes from "./routes"
import theme from './theme'

const Config = defineConfig({
  locale,
  routes,
  theme,
  outputPath: "ymir",
  hash: true,
  nodeModulesTransform: {
    type: "none",
  },
  headScripts: [{ src: '/config/config.js' } ],
  fastRefresh: {},

  // open mfsu
  // webpack5: false,
  dynamicImport: {},
  // mfsu: {},
})

export default Config
