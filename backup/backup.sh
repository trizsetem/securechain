#!/bin/bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

DOCUMENTOS_DIR="$BASE_DIR/documentos"
BACKUP_DIR="$BASE_DIR/backup"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/backup.log"
BLOCKCHAIN_SCRIPT="$BASE_DIR/blockchain/blockchain.py"

DATA="$(date +"%Y-%m-%d_%H-%M-%S")"

ARQUIVO_COMPACTADO="$BACKUP_DIR/documentos_$DATA.tar.gz"
ARQUIVO_CRIPTOGRAFADO="$BACKUP_DIR/documentos_$DATA.tar.gz.enc"

mkdir -p "$DOCUMENTOS_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"

if [ ! -f "$BLOCKCHAIN_SCRIPT" ]; then
    echo "Erro: blockchain.py não encontrado em $BLOCKCHAIN_SCRIPT"
    exit 1
fi

if [ -z "$(ls -A "$DOCUMENTOS_DIR")" ]; then
    echo "Erro: o diretório documentos está vazio."
    exit 1
fi

echo "Iniciando backup seguro..."

read -s -p "Digite a senha para criptografar o backup: " SENHA_BACKUP
echo

tar -czf "$ARQUIVO_COMPACTADO" -C "$BASE_DIR" documentos

openssl enc -aes-256-cbc -pbkdf2 -salt \
    -in "$ARQUIVO_COMPACTADO" \
    -out "$ARQUIVO_CRIPTOGRAFADO" \
    -pass pass:"$SENHA_BACKUP"

rm "$ARQUIVO_COMPACTADO"

TAMANHO="$(du -h "$ARQUIVO_CRIPTOGRAFADO" | cut -f1)"
DATA_LOG="$(date -Iseconds)"

echo "[$DATA_LOG] Backup: $ARQUIVO_CRIPTOGRAFADO | Tamanho: $TAMANHO | Status: SUCESSO" >> "$LOG_FILE"

python3 "$BLOCKCHAIN_SCRIPT" add "Backup executado com sucesso: $(basename "$ARQUIVO_CRIPTOGRAFADO") | Tamanho: $TAMANHO"

echo "Backup seguro concluído com sucesso."
echo "Arquivo criptografado: $ARQUIVO_CRIPTOGRAFADO"
echo "Tamanho: $TAMANHO"
echo "Log salvo em: $LOG_FILE"
