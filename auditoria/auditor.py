#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RELATORIOS_DIR = BASE_DIR / "relatorios"


def executar_comando(comando):
    # executa o comando do so e retorna a saída.
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            text=True,
            capture_output=True,
            timeout=15
        )

        if resultado.returncode == 0:
            return resultado.stdout.strip() or "nenhuma informacao retornada"

        return (
            "erro ao executar comando\n"
            f"codigo de retorno: {resultado.returncode}\n"
            f"erro: {resultado.stderr.strip()}"
        )

    except subprocess.TimeoutExpired:
        return "erro: tempo limite excedido ao executar o comando"

    except Exception as erro:
        return f"erro inesperado: {erro}"


def gerar_secao(titulo, comando):
    # gera uma secao formatada do relat.
    saida = executar_comando(comando)

    return f"""
=============================
{titulo}
comando executado: {comando}
==============================

{saida}

"""


def gerar_relatorio():
    # gera o relat. de auditoria do so.
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    agora = datetime.now()
    data_hora_arquivo = agora.strftime("%Y-%m-%d_%H-%M-%S")
    data_hora_relatorio = agora.strftime("%d/%m/%Y %H:%M:%S")

    nome_arquivo = f"auditoria_so_{data_hora_arquivo}.txt"
    caminho_relatorio = RELATORIOS_DIR / nome_arquivo

    conteudo = f"""
SECURECHAIN AUDIT - RELATÓRIO DE AUDITORIA DO SISTEMA OPERACIONAL

Data/hora da auditoria: {data_hora_relatorio}

Este relatório contem informações coletadas do sistema operacional
para fins de auditoria.

"""

    conteudo += gerar_secao(
        "I. USUARIOS ATUALMENTE CONECTADOS",
        "who"
    )

    conteudo += gerar_secao(
        "II. HISTORICO DE LOGINS",
        "last"
    )

    conteudo += gerar_secao(
        "III. PORTAS E SERVICOS EM ESCUTA",
        "ss -tulpn"
    )

    conteudo += gerar_secao(
        "IV. INTERFACES DE REDE E ENDEREÇOS IP",
        "ip a"
    )

    conteudo += """
=========================
FIM DO RELATÓRIO
========================
"""

    caminho_relatorio.write_text(conteudo, encoding="utf-8")

    print("relatorio de auditoria gerado com sucesso")
    print(f"arquivo: {caminho_relatorio}")


if __name__ == "__main__":
    gerar_relatorio()

    # ------------------------------------------
    # executa os comandos exigidos no enunciado: who, last, ss -tulpn e ip a, deve salvar tudo em um relatorio dentro de auditoria/relatorios/.

    # python3 auditoria.py

    # chmod +x auditoria.py
    # ./auditoria.py

    # Os dados coletados devem ser salvos em relatório datado no diretório auditoria/relatorios/.
