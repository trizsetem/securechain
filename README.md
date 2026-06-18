#### Integrantes

Beatriz Setem Ficiano - 202310321
Camille Cristofoletti Kantovitz - 202310235
Rayanne Fusato - 202310272

#### SecureChain Audit

Plataforma de auditoria baseada em blockchain desenvolvida como prova prática da disciplina de Segurança de Sistemas com Blockchain, Criptografia e Auditoria de Eventos.

---

#### Objetivo:

Desenvolver uma plataforma de auditoria que permita:

- Gerenciar usuários com diferentes níveis de acesso;
- Registrar eventos importantes em uma blockchain local;
- Monitorar a integridade de arquivos usando hash SHA-256;
- Detectar alteração, exclusão e inclusão de arquivos;
- Realizar backup compactado e criptografado;
- Gerar relatórios de auditoria do sistema operacional;
- Aplicar princípios de segurança como Zero Trust e Menor Privilégio.

---

#### Tecnologias Utilizadas:

- Linux Debian 13
- Python 3
- Bash Script
- Git e GitHub
- SHA-256
- bcrypt ou hash com salt
- OpenSSL ou GPG para criptografia de backup

---

#### Estrutura de Pastas:

A estrutura inicial do projeto vai seguir a organização solicitada no enunciado, separando os módulos por responsabilidade: blockchain, auditoria, backup, logs, documentos monitorados e usuários. Tendo o objetivo de facilitar a divisão de tarefas entre os integrantes da equipe.

---

securechain/
├── blockchain/
│ ├── blockchain.py
│ └── chain.json
│
├── auditoria/
│ ├── auditor.py
│ └── relatorios/
│
├── backup/
│ └── backup.sh
│
├── logs/
│
├── documentos/
│
├── usuarios/
│
└── README.md
