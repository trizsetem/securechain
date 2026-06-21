#!/bin/bash

# deve ser modificado de acordo com a localização do projeto no sistema
PROJETO="/home/administrador/securechain"

/usr/sbin/groupadd -f securechain_admin
/usr/sbin/groupadd -f securechain_analista
/usr/sbin/groupadd -f securechain_visitante

# usuários nos grupos
#/usr/sbin/usermod -aG securechain_admin administrador
#/usr/sbin/usermod -aG securechain_analista analista
#/usr/sbin/usermod -aG securechain_visitante visitante

# permite atravessar /home/administrador sem listar
chmod 751 /home/administrador

# raiz do projeto: todos podem entrar, mas só admin altera
chown administrador:securechain_admin "$PROJETO"
chmod 755 "$PROJETO"

# auth.py: todos podem executar para login
chown administrador:securechain_admin "$PROJETO/auth.py"
chmod 755 "$PROJETO/auth.py"

# usuários: somente administrador acessa dados sensíveis
chown -R administrador:securechain_admin "$PROJETO/usuarios"
chmod -R 770 "$PROJETO/usuarios"

chmod 660 "$PROJETO/usuarios/users.json" 2>/dev/null
chmod 660 "$PROJETO/usuarios/session.json" 2>/dev/null

# blockchain: admin escreve, analista lê
chown -R administrador:securechain_analista "$PROJETO/blockchain"
chmod -R 750 "$PROJETO/blockchain"

# documentos: admin escreve, analista lê
chown -R administrador:securechain_analista "$PROJETO/documentos"
chmod -R 750 "$PROJETO/documentos"

# auditoria: admin escreve, analista lê
chown -R administrador:securechain_analista "$PROJETO/auditoria"
chmod -R 750 "$PROJETO/auditoria"

# relatórios: visitante pode ler
chown -R administrador:securechain_visitante "$PROJETO/auditoria/relatorios"
chmod -R 750 "$PROJETO/auditoria/relatorios"

# permite visitante atravessar até relatorios
chmod 751 "$PROJETO/auditoria"

# logs: admin escreve, analista lê
chown -R administrador:securechain_analista "$PROJETO/logs"
chmod -R 750 "$PROJETO/logs"

# backup: somente administrador
chown -R administrador:securechain_admin "$PROJETO/backup"
chmod -R 700 "$PROJETO/backup"


# administradores têm acesso total a todos os diretórios
setfacl -R -m g:securechain_admin:rwx "$PROJETO/blockchain"
setfacl -R -m g:securechain_admin:rwx "$PROJETO/documentos"
setfacl -R -m g:securechain_admin:rwx "$PROJETO/auditoria"
setfacl -R -m g:securechain_admin:rwx "$PROJETO/logs"
setfacl -R -m g:securechain_admin:rwx "$PROJETO/backup"

# herda ACL para novos arquivos criados
setfacl -R -d -m g:securechain_admin:rwx "$PROJETO/blockchain"
setfacl -R -d -m g:securechain_admin:rwx "$PROJETO/documentos"
setfacl -R -d -m g:securechain_admin:rwx "$PROJETO/auditoria"
setfacl -R -d -m g:securechain_admin:rwx "$PROJETO/logs"
setfacl -R -d -m g:securechain_admin:rwx "$PROJETO/backup"
echo "Permissões aplicadas."
