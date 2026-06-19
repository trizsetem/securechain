import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CHAIN_FILE = BASE_DIR / "chain.json"


def calcular_hash(bloco):
    """
    Calcula o hash SHA-256 do bloco.
    O campo hash_atual não entra no cálculo, porque ele é o resultado final.
    """
    bloco_para_hash = bloco.copy()
    bloco_para_hash.pop("hash_atual", None)

    bloco_json = json.dumps(
        bloco_para_hash,
        sort_keys=True,
        ensure_ascii=False
    ).encode("utf-8")

    return hashlib.sha256(bloco_json).hexdigest()


def carregar_chain():
    """
    Carrega a blockchain do arquivo chain.json.
    Se o arquivo não existir, retorna lista vazia.
    """
    if not CHAIN_FILE.exists():
        return []

    try:
        with open(CHAIN_FILE, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()

            if not conteudo:
                return []

            return json.loads(conteudo)

    except json.JSONDecodeError:
        print("ALERTA: chain.json está corrompido ou com formato inválido.")
        return []


def salvar_chain(chain):
    """
    Salva a blockchain no arquivo chain.json.
    """
    with open(CHAIN_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(chain, arquivo, indent=4, ensure_ascii=False)


def criar_bloco_genese():
    """
    Cria o primeiro bloco da blockchain.
    """
    bloco = {
        "id": 0,
        "timestamp": datetime.now().isoformat(),
        "evento": "Bloco gênese criado",
        "hash_anterior": "0",
        "hash_atual": ""
    }

    bloco["hash_atual"] = calcular_hash(bloco)
    return bloco


def garantir_chain_inicializada():
    """
    Garante que a blockchain tenha pelo menos o bloco gênese.
    """
    chain = carregar_chain()

    if len(chain) == 0:
        bloco_genese = criar_bloco_genese()
        chain.append(bloco_genese)
        salvar_chain(chain)

    return chain


def adicionar_evento(evento):
    """
    Adiciona um novo evento como bloco na blockchain.
    """
    chain = garantir_chain_inicializada()

    ultimo_bloco = chain[-1]

    novo_bloco = {
        "id": ultimo_bloco["id"] + 1,
        "timestamp": datetime.now().isoformat(),
        "evento": evento,
        "hash_anterior": ultimo_bloco["hash_atual"],
        "hash_atual": ""
    }

    novo_bloco["hash_atual"] = calcular_hash(novo_bloco)

    chain.append(novo_bloco)
    salvar_chain(chain)

    print("Evento registrado na blockchain com sucesso.")
    print(f"ID do bloco: {novo_bloco['id']}")
    print(f"Evento: {novo_bloco['evento']}")
    print(f"Hash atual: {novo_bloco['hash_atual']}")


def validar_chain():
    """
    Valida a integridade da blockchain.
    Verifica:
    1. Se o hash atual de cada bloco está correto.
    2. Se o hash_anterior aponta para o hash_atual do bloco anterior.
    """
    chain = carregar_chain()

    if len(chain) == 0:
        print("Blockchain vazia.")
        return False

    for i, bloco in enumerate(chain):
        hash_recalculado = calcular_hash(bloco)

        if bloco["hash_atual"] != hash_recalculado:
            print("ALERTA: blockchain corrompida.")
            print(f"Bloco com problema: {bloco['id']}")
            print(f"Hash armazenado:   {bloco['hash_atual']}")
            print(f"Hash recalculado:  {hash_recalculado}")
            return False

        if i > 0:
            bloco_anterior = chain[i - 1]

            if bloco["hash_anterior"] != bloco_anterior["hash_atual"]:
                print("ALERTA: quebra de encadeamento detectada.")
                print(f"Bloco com problema: {bloco['id']}")
                print(f"Hash anterior esperado: {bloco_anterior['hash_atual']}")
                print(f"Hash anterior encontrado: {bloco['hash_anterior']}")
                return False

    print("Blockchain íntegra. Nenhuma adulteração detectada.")
    return True


def listar_blocos():
    """
    Lista todos os blocos da blockchain.
    """
    chain = carregar_chain()

    if len(chain) == 0:
        print("Blockchain vazia.")
        return

    for bloco in chain:
        print("-" * 60)
        print(f"ID: {bloco['id']}")
        print(f"Data/Hora: {bloco['timestamp']}")
        print(f"Evento: {bloco['evento']}")
        print(f"Hash anterior: {bloco['hash_anterior']}")
        print(f"Hash atual: {bloco['hash_atual']}")


def main():
    parser = argparse.ArgumentParser(
        description="Blockchain de auditoria do SecureChain Audit"
    )

    subparsers = parser.add_subparsers(dest="comando")

    parser_add = subparsers.add_parser("add", help="Adicionar evento na blockchain")
    parser_add.add_argument("evento", help="Descrição do evento")

    subparsers.add_parser("validate", help="Validar integridade da blockchain")
    subparsers.add_parser("list", help="Listar blocos da blockchain")
    subparsers.add_parser("init", help="Inicializar blockchain com bloco gênese")

    args = parser.parse_args()

    if args.comando == "add":
        adicionar_evento(args.evento)

    elif args.comando == "validate":
        validar_chain()

    elif args.comando == "list":
        listar_blocos()

    elif args.comando == "init":
        garantir_chain_inicializada()
        print("Blockchain inicializada com sucesso.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

