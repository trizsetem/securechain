import os
import subprocess
import json
import hashlib
import secrets
from datetime import datetime

# melhorada segurança de acesso aos diretórios
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "usuarios", "users.json")
SESSION_FILE = os.path.join(BASE_DIR, "usuarios", "session.json")
CHAIN_FILE = os.path.join(BASE_DIR, "blockchain", "chain.json")

PERFIS_VALIDOS = ["administrador", "analista", "visitante"]


# adicionado grupos do linux também
GRUPOS_LINUX = {
    "administrador": "securechain_admin",
    "analista": "securechain_analista",
    "visitante": "securechain_visitante"
}


def garantir_arquivos():
    os.makedirs(os.path.join(BASE_DIR, "usuarios"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "blockchain"), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f, indent=4)

    if not os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE, "w") as f:
            json.dump([], f, indent=4)


def gerar_hash_senha(senha, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    senha_com_salt = salt + senha
    hash_senha = hashlib.sha256(senha_com_salt.encode()).hexdigest()

    return salt, hash_senha


def carregar_usuarios():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def salvar_usuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)


def calcular_hash_bloco(bloco):
    bloco_copia = bloco.copy()
    bloco_copia.pop("hash_atual", None)

    bloco_json = json.dumps(bloco_copia, sort_keys=True)
    return hashlib.sha256(bloco_json.encode()).hexdigest()


def registrar_evento_blockchain(evento):
    with open(CHAIN_FILE, "r") as f:
        cadeia = json.load(f)

    hash_anterior = cadeia[-1]["hash_atual"] if cadeia else "0"

    bloco = {
        "id": len(cadeia) + 1,
        "timestamp": datetime.now().isoformat(),
        "evento": evento,
        "hash_anterior": hash_anterior,
        "hash_atual": ""
    }

    bloco["hash_atual"] = calcular_hash_bloco(bloco)
    cadeia.append(bloco)

    with open(CHAIN_FILE, "w") as f:
        json.dump(cadeia, f, indent=4)


def login():
    usuarios = carregar_usuarios()

    nome = input("Usuário: ").strip()
    senha = input("Senha: ").strip()

    usuario_encontrado = None

    for usuario in usuarios:
        if usuario["nome"] == nome:
            usuario_encontrado = usuario
            break

    if usuario_encontrado is None:
        registrar_evento_blockchain(f"Tentativa de acesso negada: {nome}")
        print("Acesso negado.")
        return

    salt = usuario_encontrado["salt"]
    _, hash_digitado = gerar_hash_senha(senha, salt)

    if hash_digitado == usuario_encontrado["senha_hash"]:
        sessao = {
            "usuario": usuario_encontrado["nome"],
            "perfil": usuario_encontrado["perfil"],
            "login_em": datetime.now().isoformat(),
            "ativo": True
        }

        with open(SESSION_FILE, "w") as f:
            json.dump(sessao, f, indent=4)

        registrar_evento_blockchain(
            f"login realizado: {usuario_encontrado['nome']} perfil: {usuario_encontrado['perfil']}"
        )

        print("Login realizado com sucesso.")
        print(f"Perfil ativo: {usuario_encontrado['perfil']}")

        if usuario_encontrado["perfil"] == "administrador":
            subprocess.run(["su", "-", usuario_encontrado["nome"]])
            menu_administrador()

        elif usuario_encontrado["perfil"] == "analista":
            #menu_analista()
            subprocess.run(["su", "-", usuario_encontrado["nome"]])

        elif usuario_encontrado["perfil"] == "visitante":
            #menu_visitante()
            subprocess.run(["su", "-", usuario_encontrado["nome"]])

        return

    registrar_evento_blockchain(f"Tentativa de acesso negada: {nome}")
    print("Acesso negado.")


def ver_sessao():
    if not os.path.exists(SESSION_FILE):
        print("Nenhuma sessão ativa.")
        return

    with open(SESSION_FILE, "r") as f:
        sessao = json.load(f)

    if sessao.get("ativo"):
        print("Sessão ativa:")
        print(f"Usuário: {sessao['usuario']}")
        print(f"Perfil: {sessao['perfil']}")
        print(f"Login em: {sessao['login_em']}")
    else:
        print("Nenhuma sessão ativa.")


def logout():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            sessao = json.load(f)

        sessao["ativo"] = False

        with open(SESSION_FILE, "w") as f:
            json.dump(sessao, f, indent=4)

        registrar_evento_blockchain(f"logout realizado: {sessao['usuario']}")

    print("Logout realizado.")

def menu():
    garantir_arquivos()

    while True:
        print("\n=== SecureChain Audit ===")
        print("1 - Login")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            login()

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")

def menu_administrador():
    while True:
        print("\n=== MENU ADMINISTRADOR ===")
        print("1 - Cadastrar usuário")
        print("2 - Logout")

        opcao = input("Escolha: ")

        if opcao == "1":
            subprocess.run(["python3", os.path.join(BASE_DIR, "cadastro_usuario.py")])
        elif opcao == "2":
            logout()
            break

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
