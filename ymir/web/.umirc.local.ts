import { defineConfig } from "umi"

export default defineConfig({
  define: {
    "process.env.APIURL": "/api/v1/",
  },

  // // development api proxy
  proxy: {
    "/api": {
      target: "http://192.168.13.107:9999/",
      changeOrigin: true,
      pathRewrite: { "^/api": "/api" },
    },
    '/ymir-': {
      target: "http://192.168.13.107:7777/",
      changeOrigin: true,
      pathRewrite: { 
        "^/ymir-storage": "/ymir-storage",
        "^/ymir-assets": "/ymir-assets",
        "^/ymir-models": "/ymir-models",
       },
    },
    '/socket': {
      target: 'http://192.168.13.107:9881/',
      changeOrigin: true,
      pathRewrite: {
        '^/socket': '/socket',
      }
    }
  },
  mfsu: {},
})
