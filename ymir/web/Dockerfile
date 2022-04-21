FROM node:16-alpine as builder
WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org

COPY package.json .
COPY package-lock.json .
RUN npm install --registry ${NPM_REGISTRY}
COPY . .
RUN npm run build:dev

FROM nginx:alpine
COPY --from=builder /app/ymir /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/default.conf
#COPY nginx.conf /etc/nginx/conf.d
COPY nginx.conf.template /etc/nginx/conf.d

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

