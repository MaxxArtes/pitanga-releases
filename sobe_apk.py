#!/usr/bin/env python3
"""Sobe um APK para o R2 no bucket pocket-lm. Uso: sobe_apk.py <arquivo> <versionName>

Ex.: sobe_apk.py /caminho/pitanga-v0.10.apk 0.10
-> grava em app/pitanga-v0.10.apk. O link publico no manifesto vem do refresh_modelo.py.
"""
import json
import sys

import boto3

CREDS = "/root/.config/kaggle-r2-creds.json"
BUCKET = "pocket-lm"


def main() -> None:
    arquivo, versao = sys.argv[1], sys.argv[2]
    r2 = json.load(open(CREDS))
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{r2['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=r2["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=r2["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
    key = f"app/pitanga-v{versao}.apk"
    s3.upload_file(
        arquivo, BUCKET, key,
        ExtraArgs={"ContentType": "application/vnd.android.package-archive"},
    )
    print(f"subiu: {key}")


if __name__ == "__main__":
    main()
