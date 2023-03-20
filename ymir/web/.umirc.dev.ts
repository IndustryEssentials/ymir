import { defineConfig } from "umi"
import CaseSensitivePathsPlugin  from '@umijs/case-sensitive-paths-webpack-plugin'

export default defineConfig({
  define: {
    "process.env.APIURL": "/api/v1/",
  },
  chainWebpack(memo) {
    memo.plugin('case-sensitive-module').use(CaseSensitivePathsPlugin)
  }
})
