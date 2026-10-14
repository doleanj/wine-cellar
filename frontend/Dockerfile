FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install --legacy-peer-deps
COPY . .
ARG VITE_DEV_BUILD=false
ENV VITE_DEV_BUILD=$VITE_DEV_BUILD
# Set by CI so the footer can show which build is running (after the copy, so npm install stays cached).
ARG APP_SHA=
ARG APP_BUILD_DATE=
ENV VITE_APP_SHA=$APP_SHA VITE_APP_BUILD_DATE=$APP_BUILD_DATE
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
LABEL org.opencontainers.image.source=https://github.com/doleanj/wine-cellar
ENV BACKEND_HOST=backend
EXPOSE 80
