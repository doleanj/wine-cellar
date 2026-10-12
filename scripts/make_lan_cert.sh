#!/usr/bin/env bash
# Create (once) a private LAN certificate authority and issue a server certificate for the given names.
#
#   scripts/make_lan_cert.sh <out-dir> <days> <name-or-ip>...
#   e.g. scripts/make_lan_cert.sh ~/workspace/wine-cellar-assets/tls 800 wine-cellar.nashome nashome 10.0.4.97
#
# Output (in <out-dir>):  ca.crt (install on devices, import as "intermediate" in DSM), ca.key (KEEP SECRET, never share),
#                         $BASE.crt + $BASE.key (import into DSM: Control Panel > Security > Certificate > Add > Import).
# Re-running with more names re-issues the server certificate with the SAME CA, so devices keep trusting it.
# <days> must be <= 825: Apple devices reject longer server-certificate lifetimes even from an installed CA.
# Browsers ignore the common name: every host name / IP has to be in the SAN list. A wildcard ("*.nashome") does NOT work
# for a single-label domain (OpenSSL/curl and Chrome reject it, verified), so list every site explicitly. Adding a site
# later = re-run with the extra name and re-import the certificate in DSM ("Replace an existing certificate").
# (A wildcard would work with a two-label domain such as *.nas.home.arpa.)
#   BASENAME=nashome-lan scripts/make_lan_cert.sh <dir> 800 nashome wine-cellar.nashome grafana.nashome 10.0.4.97
set -euo pipefail
[ $# -ge 3 ] || { sed -n '2,13p' "$0"; exit 1; }
OUT="$1"; DAYS="$2"; shift 2
BASE="${BASENAME:-server}"   # output file base name, e.g. BASENAME=nashome-lan
[ "$DAYS" -le 825 ] || { echo "days must be <= 825" >&2; exit 1; }
mkdir -p "$OUT"; chmod 700 "$OUT"; cd "$OUT"

# Allowed names for the CA (limits the damage if the CA key ever leaks): the first label-less domain of each name + IPs.
DOMAINS=""; IPS=""
for n in "$@"; do
  if [[ "$n" =~ ^[0-9.]+$ ]]; then IPS="$IPS $n"; else d="${n##*.}"; case " $DOMAINS " in *" $d "*) ;; *) DOMAINS="$DOMAINS $d";; esac; fi
done

if [ ! -f ca.key ]; then
  openssl genrsa -out ca.key 4096 2>/dev/null; chmod 600 ca.key
  {
    echo "[req]"; echo "distinguished_name=dn"; echo "x509_extensions=v3_ca"; echo "prompt=no"
    echo "[dn]"; echo "CN=Wine Cellar LAN CA"; echo "O=Home LAN"
    echo "[v3_ca]"; echo "basicConstraints=critical,CA:true,pathlen:0"; echo "keyUsage=critical,keyCertSign,cRLSign"
    echo "subjectKeyIdentifier=hash"
    echo "nameConstraints=critical,@nc"; echo "[nc]"
    i=0; for d in $DOMAINS; do echo "permitted;DNS.$i=$d"; i=$((i+1)); done
    echo "permitted;IP.0=10.0.0.0/255.0.0.0"; echo "permitted;IP.1=192.168.0.0/255.255.0.0"; echo "permitted;IP.2=172.16.0.0/255.240.0.0"
  } > ca.cnf
  openssl req -x509 -new -key ca.key -sha256 -days 3650 -config ca.cnf -out ca.crt
  echo "created CA: $OUT/ca.crt"
fi

openssl genrsa -out $BASE.key 2048 2>/dev/null; chmod 600 $BASE.key
{
  echo "[req]"; echo "distinguished_name=dn"; echo "req_extensions=v3_req"; echo "prompt=no"
  echo "[dn]"; echo "CN=$1"
  echo "[v3_req]"; echo "subjectAltName=@san"
  echo "[san]"; d=0; ip=0
  for n in "$@"; do if [[ "$n" =~ ^[0-9.]+$ ]]; then echo "IP.$ip=$n"; ip=$((ip+1)); else echo "DNS.$d=$n"; d=$((d+1)); fi; done
} > $BASE.cnf
openssl req -new -key $BASE.key -config $BASE.cnf -out $BASE.csr
{
  echo "basicConstraints=critical,CA:false"; echo "keyUsage=critical,digitalSignature,keyEncipherment"
  echo "extendedKeyUsage=serverAuth"; echo "subjectKeyIdentifier=hash"; echo "authorityKeyIdentifier=keyid"
  echo "subjectAltName=@san"; sed -n '/^\[san\]/,$p' $BASE.cnf
} > $BASE.ext
openssl x509 -req -in $BASE.csr -CA ca.crt -CAkey ca.key -CAcreateserial -sha256 -days "$DAYS" -extfile $BASE.ext -out $BASE.crt 2>/dev/null
rm -f $BASE.csr
openssl rsa -in $BASE.key -traditional -out $BASE-rsa.key 2>/dev/null; chmod 600 $BASE-rsa.key   # classic PEM format, for importers that reject PKCS#8
openssl verify -CAfile ca.crt $BASE.crt
openssl x509 -in $BASE.crt -noout -subject -issuer -dates -ext subjectAltName
