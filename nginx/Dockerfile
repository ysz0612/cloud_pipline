FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ ./

ARG VITE_API_URL=/api/image-rag
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build


FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=frontend-builder \
    /frontend/dist \
    /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]