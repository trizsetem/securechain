import os
import json
import hashlib
import secrets
from datetime import datetime

USERS_FILE = "usuarios/users.json"
SESSION_FILE = "usuarios/session.json"
CHAIN_FILE = "blockchain/chain.json"

PERFIS_VALIDOS = ["administrador", "analista", "visitante"]


def garantir_arquivos():
    os.makedirs("usuarios", exist_ok=True)
    os.makedirs("blockchain", exist_ok=True)

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


def cadastrar_usuario():
    usuarios = carregar_usuarios()

    nome = input("Nome do usuário: ").strip()
    senha = input("Senha: ").strip()
    perfil = input("Perfil [administrador/analista/visitante]: ").strip().lower()

    if perfil not in PERFIS_VALIDOS:
        print("Perfil inválido.")
        return

    for usuario in usuarios:
        if usuario["nome"] == nome:
            print("Usuário já existe.")
            return

    salt, hash_senha = gerar_hash_senha(senha)

    novo_usuario = {
        "nome": nome,
        "perfil": perfil,
        "salt": salt,
        "senha_hash": hash_senha,
        "criado_em": datetime.now().isoformat()
    }

    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)

    registrar_evento_blockchain(f"usuário criado: {nome} perfil: {perfil}")

    print("Usuário cadastrado com sucesso.")


def login():
    usuarios = carregar_usuarios()

    nome = input("Usuário: ").strip()
    senha = input("Senha: ").strip()

    for usuario in usuarios:
        if usuario["nome"] == nome:
            salt = usuario["salt"]
            _, hash_digitado = gerar_hash_senha(senha, salt)

            if hash_digitado == usuario["senha_hash"]:
                sessao = {
                    "usuario": usuario["nome"],
                    "perfil": usuario["perfil"],
                    "login_em": datetime.now().isoformat(),
                    "ativo": True
                }

                with open(SESSION_FILE, "w") as f:
                    json.dump(sessao, f, indent=4)

                registrar_evento_blockchain(
                    f"login realizado: {usuario['nome']} perfil: {usuario['perfil']}"
                )

                print("Login realizado com sucesso.")
                print(f"Perfil ativo: {usuario['perfil']}")
                return

    registrar_evento_blockchain(f"tentativa de acesso negada: {nome}")
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
        print("\n=== SecureChain Audit - Autenticação ===")
        print("1 - Cadastrar usuário")
        print("2 - Login")
        print("3 - Ver sessão ativa")
        print("4 - Logout")
        print("0 - Sair")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            login()
        elif opcao == "3":
            ver_sessao()
        elif opcao == "4":
            logout()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
