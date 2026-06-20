import os
import json
import hashlib
from datetime import datetime


DOCUMENTOS_DIR = "../documentos"
HASHES_FILE = "hashes_documentos.json"
CHAIN_FILE = "../blockchain/chain.json"


def criar_estrutura():
    os.makedirs(DOCUMENTOS_DIR, exist_ok=True)
    os.makedirs("../auditoria", exist_ok=True)
    os.makedirs("../blockchain", exist_ok=True)

    if not os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, "w") as arquivo:
            json.dump({}, arquivo, indent=4)

    if not os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE, "w") as arquivo:
            json.dump([], arquivo, indent=4)


def hash_arquivo(caminho):
    sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo:
        while True:
            parte = arquivo.read(4096)
            if not parte:
                break
            sha256.update(parte)

    return sha256.hexdigest()


def ler_json(caminho, valor_padrao):
    try:
        with open(caminho, "r") as arquivo:
            return json.load(arquivo)
    except:
        return valor_padrao


def salvar_json(caminho, dados):
    with open(caminho, "w") as arquivo:
        json.dump(dados, arquivo, indent=4)


def hash_bloco(bloco):
    dados = {
        "id": bloco["id"],
        "timestamp": bloco["timestamp"],
        "evento": bloco["evento"],
        "hash_anterior": bloco["hash_anterior"]
    }

    texto = json.dumps(dados, sort_keys=True)
    return hashlib.sha256(texto.encode()).hexdigest()


def registrar_na_blockchain(evento):
    cadeia = ler_json(CHAIN_FILE, [])

    if len(cadeia) == 0:
        hash_anterior = "0"
    else:
        hash_anterior = cadeia[-1]["hash_atual"]

    bloco = {
        "id": len(cadeia) + 1,
        "timestamp": datetime.now().isoformat(),
        "evento": evento,
        "hash_anterior": hash_anterior,
        "hash_atual": ""
    }

    bloco["hash_atual"] = hash_bloco(bloco)
    cadeia.append(bloco)

    salvar_json(CHAIN_FILE, cadeia)


def mapear_documentos():
    resultado = {}

    for pasta_atual, _, arquivos in os.walk(DOCUMENTOS_DIR):
        for nome_arquivo in arquivos:
            caminho_completo = os.path.join(pasta_atual, nome_arquivo)
            caminho_relativo = os.path.relpath(caminho_completo, DOCUMENTOS_DIR)

            resultado[caminho_relativo] = hash_arquivo(caminho_completo)

    return resultado


def criar_base_inicial():
    hashes = mapear_documentos()
    salvar_json(HASHES_FILE, hashes)

    registrar_na_blockchain("base inicial de hashes dos documentos criada")

    print("Base inicial criada com sucesso.")
    print(f"Total de arquivos monitorados: {len(hashes)}")


def verificar_documentos():
    hashes_antigos = ler_json(HASHES_FILE, {})
    hashes_atuais = mapear_documentos()

    eventos = []

    for arquivo in hashes_antigos:
        if arquivo not in hashes_atuais:
            eventos.append(f"arquivo excluído: {arquivo}")
        elif hashes_antigos[arquivo] != hashes_atuais[arquivo]:
            eventos.append(f"arquivo alterado: {arquivo}")

    for arquivo in hashes_atuais:
        if arquivo not in hashes_antigos:
            eventos.append(f"arquivo incluído: {arquivo}")

    if len(eventos) == 0:
        print("Nenhuma inconsistência detectada.")
        return

    print("\nALERTA DE INTEGRIDADE:")
    for evento in eventos:
        print(f"- {evento}")
        registrar_na_blockchain(evento)

    salvar_json(HASHES_FILE, hashes_atuais)
    print("\nBase de hashes atualizada após a verificação.")


def menu():
    criar_estrutura()

    while True:
        print("\n=== Módulo I.4 - Integridade de Arquivos ===")
        print("1 - Criar base inicial de hashes")
        print("2 - Verificar integridade dos documentos")
        print("0 - Sair")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            criar_base_inicial()
        elif opcao == "2":
            verificar_documentos()
        elif opcao == "0":
            print("Saindo do módulo I.4.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
