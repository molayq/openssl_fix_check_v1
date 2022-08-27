import glob
import os
import sys
from datetime import datetime, date

from cryptography.hazmat.primitives.serialization import pkcs12
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml

from sns import SnsHelper

clients = {
    "op": {
        "name": "op",
        "environment": ['test', 'acc', 'prod']
    },
    "rabo-rn": {
        "name": "rabo-rn",
        "environment": ['test', 'acc', 'prod']
    },
    "rabo-au": {
        "name": "rabo-au",
        "environment": ['test', 'acc', 'prod']
    },
    "nordea": {
        "name": "nordea",
        "environment": ['test', 'acc', 'prod']
    },
    "lbbw": {
        "name": "lbbw",
        "environment": ['test', 'acc', 'prod']
    },
    "kbc": {
        "name": "kbc",
        "environment": ['test', 'acc', 'prod']
    },
    "seb": {
        "name": "seb",
        "environment": ['test', 'acc', 'prod']
    }
}


def checkDate(cert):
    return abs((cert - datetime.now()))


def getFixTLSExpirationDates(accessKey='', secret=''):
    closeDateCertExpirations = []
    savedFilePath = "fixCertsExpiration.txt"
    maxExpirationDaysCheck = 60

    if (os.path.exists(savedFilePath)):
        os.remove(savedFilePath)

    for client in clients.values():
        for env in client["environment"]:
            try:

                with open(
                        r'/Users/vladonetiu//ansible/environments/%s/%s/secret/secret_vars.yml' % (
                                client["name"], env)) as file:
                    secretList = yaml.load(file, Loader=yaml.FullLoader)
                    if (client["name"] == 'seb' and env == 'prod'):
                        passwordBase = secretList["easytrade"]["fixcommunication"]["web1"]["session"][
                            "pfx_password"].encode()
                        certPath = "/Users/vladonetiu/repos/easytrade-deployment/ansible/environments/%s/%s/files/webapp/app/lib/easytrade-TREASURUP1-fix-client.pfx" % (
                            client["name"], env)
                    else:
                        passwordBase = secretList['fix']['pfx_password']
                        if passwordBase is None:  # some pfx dont have any import pass
                            passwordBase = ''.encode()
                        else:
                            passwordBase = passwordBase.encode()
                        certPath = "/Users/vladonetiu//ansible/environments/%s/%s/files/webapp/app/lib/*.pfx" % (
                            client["name"], env)

                    with open(glob.glob(certPath)[0], "rb") as f:
                        # print(passwordBase)
                        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(f.read(),
                                                                                                             b"%s" % passwordBase)
                    certDateToString = str(certificate.not_valid_after)

                    f = open(savedFilePath, "a")
                    print(client["name"] + env + " " + certDateToString)

                    if (int(checkDate(certificate.not_valid_after).days) < maxExpirationDaysCheck):
                        f.write(
                            "ALERT -" + client["name"] + env + " " + certDateToString + "->Time left from now: " + str(
                                checkDate(certificate.not_valid_after)) + "\n")
                        closeDateCertExpirations.append(
                            "ALERT -" + client["name"] + env + " " + certDateToString + "->Time left from now: " + str(
                                checkDate(certificate.not_valid_after)))

                    f.write(client["name"] + env + " " + certDateToString + "->Time left from now: " + str(
                        checkDate(certificate.not_valid_after)) + "\n")

            except Exception as e:
                print("Not found", e)
                f.write(client["name"] + env + " " + "error on " + str(e) + '\n')
    f.close()

    if closeDateCertExpirations and accessKey and secret:
        SnsHelper.trigger(accessKey, secret, 'FIX TLS CERTIFICATES - EXPIRATION DATE', closeDateCertExpirations)
    else:
        print("SNS Alert not enabled")

    return closeDateCertExpirations


def main():
    start = time()
    try:
        if sys.argv[1] == 'sns':
            aws_access_key = sys.argv[2]
            aws_secret_key = sys.argv[3]
            getFixTLSExpirationDates(aws_access_key, aws_secret_key)
    except:
        getFixTLSExpirationDates()

    print(f'Time taken: {time() - start}')


if __name__ == "__main__":
    main()
