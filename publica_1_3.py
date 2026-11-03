#!/usr/bin/env python3
"""Publica a 1.3-beta no canal: atualiza releases.json (versao, changelog, links
presigned do APK e do modelo) e faz commit+push no pitanga-releases."""
import json
import subprocess
import sys

sys.path.insert(0, "/opt/pitanga-releases")
from refresh_modelo import chave_do_url, presign  # noqa: E402

REPO = "/opt/pitanga-releases"
CAMINHO = f"{REPO}/releases.json"
VERSION_CODE = 105
VERSION_NAME = "1.3-beta"
MUDOU = [
    "Auto-preenchimento completo para cadastro de concurso e afins: filiação, órgão e UF do RG, data de "
    "emissão, naturalidade, nacionalidade, sexo, estado civil, escolaridade e endereço separado (rua, número, "
    "complemento, bairro). Listas suspensas são escolhidas sozinhas.",
    "Meus dados: botão Ler da CNH (foto ou PDF) que mostra o que leu e só salva o que você marcar.",
    "Cadastro com senha: o app preenche o resto e deixa a senha para você.",
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
        f"{VERSION_NAME} (versionCode {VERSION_CODE}): autopreenchimento de cadastro completo")
    git("push", "--quiet")
    print("publicado")


if __name__ == "__main__":
    main()
