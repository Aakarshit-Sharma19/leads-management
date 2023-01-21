FROM nginx:stable-alpine
ENV NGINX_CERTS_DIR=/etc/nginx/certificates
RUN rm /etc/nginx/conf.d/default.conf
# Generate Certificates
RUN apk add --no-cache openssl && mkdir -p $NGINX_CERTS_DIR && \
    openssl req -newkey rsa:2048 -nodes -keyout $NGINX_CERTS_DIR/key.pem -x509 -days 365 -out $NGINX_CERTS_DIR/certificate.pem \
    -subj "/C=IN/ST=Karnataka/L=Bengaluru/O=NA(Individual)/OU=Aakarshit Sharma/CN=gaming.freaks.utubechannel@gmail.com"

COPY nginx.conf /etc/nginx/conf.d