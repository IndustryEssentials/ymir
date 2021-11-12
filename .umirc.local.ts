import { defineConfig } from "umi"

export default defineConfig({
  define: {
    "process.env.APIURL": "http://localhost:8000/api/v1/",
  },

  // // development api proxy
  proxy: {
    "/api": {
      target: "http://192.168.13.107:8088/",
      changeOrigin: true,
      pathRewrite: { "^/api": "/api" },
    },
    '/ymir-': {
      target: "http://192.168.13.107:8888/",
      changeOrigin: true,
      pathRewrite: { 
        "^/ymir-storage": "/ymir-storage",
        "^/ymir-assets": "/ymir-assets",
        "^/ymir-models": "/ymir-models",
       },
    }
  },
  mfsu: {},
})
