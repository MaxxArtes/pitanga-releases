#!/usr/bin/env python3
"""Publica a 1.4-beta no canal: atualiza releases.json (versao, changelog, links
presigned do APK e do modelo) e faz commit+push no pitanga-releases."""
import json
import subprocess
import sys

sys.path.insert(0, "/opt/pitanga-releases")
from refresh_modelo import chave_do_url, presign  # noqa: E402

REPO = "/opt/pitanga-releases"
CAMINHO = f"{REPO}/releases.json"
VERSION_CODE = 106
VERSION_NAME = "1.4-beta"
MUDOU = [
    "Meus dados: Ler documento aceita vários de uma vez (foto, câmera ou PDF): RG, CIN, CNH e comprovante de "
    "residência. Mostra de qual documento veio cada dado, pede para escolher quando dois discordam e destaca o que "
    "foi lido com dúvida. A foto não fica guardada.",
    "Colar meus dados: cole uma ficha, mensagem ou o texto exportado da extensão e a PitaIA separa o que é cada coisa.",
    "Base para sincronizar com a sua conta Google (vem na próxima versão).",
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
        f"{VERSION_NAME} (versionCode {VERSION_CODE}): ler documentos e colar dados")
    git("push", "--quiet")
    print("publicado")


if __name__ == "__main__":
    main()
