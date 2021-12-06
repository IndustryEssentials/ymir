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
  // chainWebpack(config, { env, webpack, createCSSRule }) {
    // gzip
    // config.when(isEnvProduction, (config) => {
    //   config
    //     .plugin("compression-webpack-plugin")
    //     .use(CompressionWebpackPlugin, [
    //       {
    //         filename: "[path].gz[query]",
    //         algorithm: "gzip",
    //         test: new RegExp("\\.(js|css)$"),
    //         threshold: 10240,
    //         minRatio: 0.8,
    //       },
    //     ]);
    // });
  // },
  fastRefresh: {},

  // open mfsu
  webpack5: {},
  dynamicImport: {},
  // mfsu: {},
})

export default Config
