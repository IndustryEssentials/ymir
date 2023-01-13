import { defineConfig } from 'umi'
import locale from './locale'
import routes from './routes'
import theme from './theme'

const Config = defineConfig({
  locale,
  routes,
  theme,
  outputPath: 'ymir',
  hash: true,
  nodeModulesTransform: {
    type: 'none',
  },
  metas: [
    { httpEquiv: 'Cache-Control', content: 'no-cache, no-store, must-revalidate' },
    { httpEquiv: 'Pragma', content: 'no-cache' },
    { httpEquiv: 'Expires', content: '0' },
  ],
  headScripts: [{ src: '/config/config.js' }],
  fastRefresh: {},
  dynamicImport: {},
})

export default Config
