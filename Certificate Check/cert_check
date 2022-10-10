#!/usr/bin/env bash

# Check and Combine Cert - Part of the Hawdon Script family
# Oh no, it's yet another Hawdon Script!

# set -x

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Colour

VERSION='0.2.1'

printf "Certificate chain checker V%s\n" "${VERSION}"

printf "Checking for OpenSSL...\r"
if command -v openssl >/dev/null 2>&1 ; then
        opensslversion=$(openssl version)
        printf "Checking for OpenSSL... %bPASS%b (%s)\n" "${GREEN}" "${NC}" "${opensslversion}"
else
        printf "Checking for OpenSSL... %bFAIL%b" "${RED}" "${NC}"
        exit 1
fi

while getopts ":b:c:i:k:r:o:" options; do
        case "${options}" in
                b)
                        bundle=${OPTARG}
                        ;;
                c)
                        cert=$(cat "${OPTARG}")
                        ;;
                i)
                        intermediate=$(cat "${OPTARG}")
                        ;;
                k)
                        key=$(cat "${OPTARG}")
                        ;;
                r)
                        root=$(cat "${OPTARG}")
                        ;;
                o)
                        output=${OPTARG}
                        ;;
                *)
                        # usage
                        ;;
        esac
done

shift "$(( OPTIND - 1))"

if [ -n "$bundle" ]; then
        if [[ ${OSTYPE} == "darwin"* ]]; then
                printf "MacOS detected, checking for gsed...\r"
                if command -v gsed >/dev/null 2>&1 ; then
                        SED=$(command -v gsed)
                        printf "MacOS detected, checking for gsed... %bPASS%b\n" "${GREEN}" "${NC}"
                else
                        printf "MacOS detected, checking for gsed... %bFAIL%b\n" "${RED}" "${NC}"
                        exit 1
                fi
        else
                SED=$(command -v sed)
        fi

        c=0
        OLDIFS=$IFS; IFS=';' blocks=$("${SED}" -n '/-----BEGIN /,/-----END/ {/-----BEGIN / s/^/\;/; p}'  "${bundle}");
        for block in ${blocks#;}; do 
            # echo $block | openssl x509 -noout -subject -in -
            bundleCert[c++]=$(printf "%s" "${block}")
        done; IFS=$OLDIFS

        if [ -n "${bundleCert[0]}" ]; then
                cert="${bundleCert[0]}"
        fi
        if [ -n "${bundleCert[1]}" ]; then
                intermediate="${bundleCert[1]}"
        fi
        if [ -n "${bundleCert[2]}" ]; then
                root="${bundleCert[2]}"
        fi
fi

if [ -n "$bundle" ] && [ -n "$key" ]; then
        printf "Using bundle and key\n"
elif [ -n "$cert" ] && [ -n "$intermediate" ] && [ -n "$key" ]; then
        printf "Using separate certs\n"
else
        echo 'Missing required arguments (-c, -i, or -b), and/or -k.' >&2
        exit 1
fi

if [ -n "$root" ] ; then
        checkroot=true
fi

if [ -n "$output" ] ; then
        combine=true
fi

printf "Checking Cert's Intermediate...\r"
certIssuerHash=$(printf "%s" "${cert}" | openssl x509 -issuer_hash -noout)
intermediateHash=$(printf "%s" "${intermediate}" | openssl x509 -hash -noout)

if [ "${certIssuerHash}" == "${intermediateHash}" ] ; then
        printf "Checking Cert's Intermediate... %bPASS%b\n" "${GREEN}" "${NC}"
else
        printf "Checking Cert's Intermediate... %bFAIL%b\n" "${RED}" "${NC}"
        exit 1
fi

if [ "${checkroot}" ] ; then
        printf "Checking Intermediate's Root...\r"
        intermediateIssuerHash=$(printf "%s" "${intermediate}" | openssl x509 -issuer_hash -noout)
        rootHash=$(printf "%s" "${root}" | openssl x509 -hash -noout)
        if [ "${intermediateIssuerHash}" == "${rootHash}" ] ; then
                printf "Checking Intermediate's Root... %bPASS%b\n" "${GREEN}" "${NC}"
        else
                printf "Checking Intermediate's Root... %bFAIL%b\n" "${RED}" "${NC}"
                exit 1
        fi

fi

printf "Checking Cert matches Key...\r"

certModulusHash=$(printf "%s" "${cert}" | openssl x509 -noout -modulus)
keyModulusHash=$(printf "%s" "${key}" | openssl rsa -noout -modulus)

if [ "${certModulusHash}" == "${keyModulusHash}" ] ; then
        printf "Checking Cert matches Key... %bPASS%b\n" "${GREEN}" "${NC}"
else
        printf "Checking Cert matches Key... %bFAIL%b\n" "${RED}" "${NC}"
        exit 1
fi

if [ "${combine}" ] ; then
        printf "All checks passed, writing combined file...\n"
        
        if [ "${checkroot}" ]; then
                cat "${cert}" "${intermediate}" "${root}" > "${output}"
        else
                cat "${cert}" "${intermediate}" > "${output}"
        fi

else
        printf "All checks passed, no output specified. \n"

fi

printf "Complete\n"
