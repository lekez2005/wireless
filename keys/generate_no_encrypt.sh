KEYNAME="server.key"
CERT="server.crt"
openssl req -nodes -new -x509 -keyout $KEYNAME -out $CERT
