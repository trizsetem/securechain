#!/usr/bin/env python3
import json
import hashlib
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CHAIN_PATH = BASE_DIR / "chain.json"



class Blockchain:
    def __init__(self):
        self.chain = self.carregar_chain()

        if not self.chain:
            self.criar_bloco_genesis()

    def carregar_chain(self):

        # carrega a blockchain salva no arquivo chain.json

        if not CHAIN_PATH.exists():
            return []

        try:
            with open(CHAIN_PATH, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except json.JSONDecodeError:
            print("erro: chain.json ta corrompido ou em formato invalido")
            return []
        except Exception as erro:
            print(f"erro ao carregar blockchain: {erro}")
            return []

    def salvar_chain(self):

        # salva a blockchain no arquivo chain.json

        with open(CHAIN_PATH, "w", encoding="utf-8") as arquivo:
            json.dump(self.chain, arquivo, indent=4, ensure_ascii=False)

    def calcular_hash(self, bloco):

        # calcula o hash SHA-256 de um bloco

        bloco_copia = bloco.copy()
        bloco_copia.pop("hash_atual", None)

        bloco_json = json.dumps(
            bloco_copia,
            sort_keys=True,
            ensure_ascii=False
        )

        return hashlib.sha256(bloco_json.encode("utf-8")).hexdigest()

    def criar_bloco_genesis(self):
        # cria o primeiro bloco da cadeia

        bloco = {
            "id": 0,
            "timestamp": datetime.now().isoformat(),
            "evento": "bloco genesis criado",
            "hash_anterior": "0"
        }

        bloco["hash_atual"] = self.calcular_hash(bloco)

        self.chain.append(bloco)
        self.salvar_chain()

    def adicionar_bloco(self, evento):
        # adiciona um novo bloco na blockchain

        ultimo_bloco = self.chain[-1]

        novo_bloco = {
            "id": len(self.chain),
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            "hash_anterior": ultimo_bloco["hash_atual"]
        }

        novo_bloco["hash_atual"] = self.calcular_hash(novo_bloco)

        self.chain.append(novo_bloco)
        self.salvar_chain()

        print("bloco adicionado")
        print(f"evento registrado: {evento}")


    def validar_integridade(self):

        # valida a integridade da blockchain

        print("\nvalidando a blockchain..\n")

        if not self.chain:
            print("alerta: blockchain vazia")
            return False

        campos_obrigatorios = [
            "id",
            "timestamp",
            "evento",
            "hash_anterior",
            "hash_atual"
        ]

        cadeia_valida = True

        for indice, bloco in enumerate(self.chain):
            print(f"validando bloco {indice}...")

            for campo in campos_obrigatorios:
                if campo not in bloco:
                    print("ALERTA DE INTEGRIDADE")
                    print(f"bloco corrompido: {indice}")
                    print(f"campo obrigatorio ausente: {campo}\n")
                    cadeia_valida = False
                    continue

            if not all(campo in bloco for campo in campos_obrigatorios):
                continue

            hash_recalculado = self.calcular_hash(bloco)

            if bloco["hash_atual"] != hash_recalculado:
                print("ALERTA DE INTEGRIDADE")
                print(f"bloco corrompido: {indice}")
                print("motivo: hash armazenado diferente do hash recalculado")
                print(f"hash armazenado:   {bloco['hash_atual']}")
                print(f"hash recalculado:  {hash_recalculado}\n")
                cadeia_valida = False

            if bloco["id"] != indice:
                print("ALERTA DE INTEGRIDADE")
                print(f"bloco corrompido: {indice}")
                print("motivo: ID do bloco fora da sequencia esperada")
                print(f"ID encontrado: {bloco['id']}")
                print(f"ID esperado:   {indice}\n")
                cadeia_valida = False

            if indice == 0:
                if bloco["hash_anterior"] != "0":
                    print("ALERTA DE INTEGRIDADE")
                    print("bloco genesis corrompido.")
                    print("motivo: hash_anterior do bloco genesis deveria ser '0'\n")
                    cadeia_valida = False
            else:
                bloco_anterior = self.chain[indice - 1]

                if bloco["hash_anterior"] != bloco_anterior.get("hash_atual"):
                    print("ALERTA DE ENCADEAMENTO")
                    print(f"bloco corrompido: {indice}")
                    print("motivo: hash_anterior não corresponde ao hash_atual do bloco anterior")
                    print(f"hash anterior salvo no bloco atual: {bloco['hash_anterior']}")
                    print(f"hash atual do bloco anterior:       {bloco_anterior.get('hash_atual')}\n")
                    cadeia_valida = False

        if cadeia_valida:
            print("blockchain valida. nenhuma adulteracao encontrada.")
        else:
            print("blockchain invalida. encontrado inconsistencias.")

        return cadeia_valida

    def listar_blocos(self):

        #  exibe todos os blocos da blockchain
        for bloco in self.chain:
            print(json.dumps(bloco, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    blockchain = Blockchain()

    while True:
        print("\n===== SecureChain Audit - blockchain =====")
        print("1. adicionar bloco de teste")
        print("2. listar blocos")
        print("3. validar integridade da blockchain")
        print("0. sair")

        opcao = input("escolha uma opcao: ").strip()

        if opcao == "1":
            evento = input("digite o evento: ").strip()

            if evento:
                blockchain.adicionar_bloco(evento)
            else:
                print("evento nao pode ser vazio.")

        elif opcao == "2":
            blockchain.listar_blocos()

        elif opcao == "3":
            blockchain.validar_integridade()

        elif opcao == "0":
            print("encerrando...")
            break

        else:
            print("opcao invalida.")

            # ------------------
            # python3 blockchain/blockchain.py
            # 
