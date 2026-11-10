FROM nginx:1.27-alpine

COPY client /usr/share/nginx/html
COPY deploiement/frontend-container.conf /etc/nginx/conf.d/default.conf

EXPOSE 80