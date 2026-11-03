#!/usr/bin/env python3
"""Publica a 1.4.1-beta no canal: atualiza releases.json (versao, changelog, links
presigned do APK e do modelo) e faz commit+push no pitanga-releases."""
import json
import subprocess
import sys

sys.path.insert(0, "/opt/pitanga-releases")
from refresh_modelo import chave_do_url, presign  # noqa: E402

REPO = "/opt/pitanga-releases"
CAMINHO = f"{REPO}/releases.json"
VERSION_CODE = 107
VERSION_NAME = "1.4.1-beta"
MUDOU = [
    "Colar meus dados entende fichas do jeito que a gente escreve: com marcadores, comentários depois do valor "
    "(\"SESP. Se for uma lista...\") e rótulos curtos como Número e UF, decididos pelo campo de cima "
    "(Número depois do RG é o RG; depois do Endereço é o da casa).",
    "Endereço inteiro numa linha é separado em rua, número, complemento, bairro, cidade, UF e CEP.",
]


def git(*args):
    subprocess.run(["git", "-C", REPO, *args], check=True)


def main():
    git("pull", "--quiet", "--ff-only")
    m = json.load(open(CAMINHO))
    assert m["versionCode"] < VERSION_CODE, f"manifesto ja esta em {m['versionCode']}"
    m["versionCode"] = VERSION_CODE
    m["versionName"] = VERSION_NAME
    m["apk"] = presign(f"app/pitanga-v{VERSION_NAME}.apk")
    m["modeloUrl"] = presign(chave_do_url(m["modeloUrl"]))
    m["releases"] = [{"versao": VERSION_NAME, "mudou": MUDOU}] + m["releases"]
    with open(CAMINHO, "w") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")
    git("add", "releases.json")
    git("commit", "--quiet", "-m",
        f"{VERSION_NAME} (versionCode {VERSION_CODE}): colar dados corrigido")
    git("push", "--quiet")
    print("publicado")


if __name__ == "__main__":
    main()
