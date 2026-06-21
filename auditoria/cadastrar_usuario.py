import os                                                                                                                                                                   
import json                                                                                                                                                                 
import hashlib                                                                                                                                                              
import secrets                                                                                                                                                              
import subprocess                                                                                                                                                           
from datetime import datetime                                                                                                                                               
                                                                                                                                                                            
                                                                                                                                                                            
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                                                                                                      
                                                                                                                                                                            
USERS_FILE = os.path.join(BASE_DIR, "usuarios", "users.json")                                                                                                               
SESSION_FILE = os.path.join(BASE_DIR, "usuarios", "session.json")                                                                                                           
CHAIN_FILE = os.path.join(BASE_DIR, "blockchain", "chain.json")                                                                                                             
                                                                                                                                                                            
PERFIS_VALIDOS = ["administrador", "analista", "visitante"]                                                                                                                 
                                                                                                                                                                            
GRUPOS_LINUX = {                                                                                                                                                            
    "administrador": "securechain_admin",                                                                                                                                   
    "analista": "securechain_analista",                                                                                                                                     
    "visitante": "securechain_visitante"                                                                                                                                    
}


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


def criar_usuario_linux(nome, perfil):
    grupo = GRUPOS_LINUX[perfil]

    subprocess.run(["/usr/sbin/groupadd", "-f", grupo], check=False)

    existe = subprocess.run(
        ["id", nome],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if existe.returncode != 0:
        subprocess.run(["/usr/sbin/useradd", "-m", "-s", "/bin/bash", nome], check=True)

    subprocess.run(["/usr/sbin/usermod", "-aG", grupo, nome], check=True)


def cadastrar_usuario():
    usuarios = carregar_usuarios()

    nome = input("Nome do usuário Linux/Python: ").strip()
    senha = input("Senha do sistema Python: ").strip()
    perfil = input("Perfil [administrador/analista/visitante]: ").strip().lower()

    if perfil not in PERFIS_VALIDOS:
        print("Perfil inválido.")
        return

    for usuario in usuarios:
        if usuario["nome"] == nome:
            print("Usuário já existe.")
            return

    criar_usuario_linux(nome, perfil)

    salt, hash_senha = gerar_hash_senha(senha)

    novo_usuario = {
        "nome": nome,
        "perfil": perfil,
        "grupo_linux": GRUPOS_LINUX[perfil],
        "salt": salt,
        "senha_hash": hash_senha,
        "criado_em": datetime.now().isoformat()
    }

    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)

    registrar_evento_blockchain(
        f"usuário criado: {nome} perfil: {perfil} grupo_linux: {GRUPOS_LINUX[perfil]}"
    )

    print("Usuário cadastrado com sucesso.")


if __name__ == "__main__":
    cadastrar_usuario()
