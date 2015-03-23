#! /bin/bash


KEYNAME="server.key"
echo "Generating key $KEYNAME"
openssl genrsa -des3 -out $KEYNAME 1024

CSR="server.csr"
echo "Generate certificate request $CSR"
openssl req -new -key $KEYNAME -out $CSR

CERT="server.crt"
echo "Generating certificate $CERT"
openssl x509 -req -days 365 -in $CSR -signkey $KEYNAME -out $CERT
