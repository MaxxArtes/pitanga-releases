#!/usr/bin/env python3
"""Renova o link presigned do modelo no manifesto publico (releases.json) e faz push.

O presigned do R2 dura no maximo 7 dias; o timer roda a cada 3 dias, entao o link
nunca expira pros usuarios. So mexe em modeloUrl — versao/changelog sao editados a mao
quando sai uma versao nova do app.
"""
import json
import os
import subprocess

import boto3

REPO = "/opt/pitanga-releases"
CREDS = "/root/.config/kaggle-r2-creds.json"
BUCKET = "pocket-lm"
KEY_MODELO = "app/pitanga-v8-q4_k_m.gguf"


def _s3():
    r2 = json.load(open(CREDS))
    return boto3.client(
        "s3",
        endpoint_url=f"https://{r2['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=r2["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=r2["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


def presign(key: str) -> str:
    return _s3().generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=7 * 24 * 3600
    )


def git(*args) -> None:
    subprocess.run(["git", "-C", REPO, *args], check=True)


def main() -> None:
    git("pull", "--quiet", "--ff-only")
    caminho = os.path.join(REPO, "releases.json")
    m = json.load(open(caminho))
    m["modeloUrl"] = presign(KEY_MODELO)
    # APK tambem no R2 (rapido no BR): a chave segue a versao publicada no manifesto.
    m["apk"] = presign(f"app/pitanga-v{m['versionName']}.apk")
    with open(caminho, "w") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")
    mudou = subprocess.run(
        ["git", "-C", REPO, "diff", "--quiet", "releases.json"]
    ).returncode != 0
    if mudou:
        git("add", "releases.json")
        git("commit", "--quiet", "-m", "cron: renova link do modelo (presigned R2, 7 dias)")
        git("push", "--quiet")
        print("modeloUrl renovado e publicado")
    else:
        print("sem mudanca")


if __name__ == "__main__":
    main()
