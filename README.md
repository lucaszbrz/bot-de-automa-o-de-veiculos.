🤖 Bot de Locadora de Carros – Discord

Este projeto é um bot para Discord desenvolvido em Python, com foco em lógica de programação, estruturas de dados e manipulação de arquivos JSON.
O bot simula o funcionamento básico de uma locadora de veículos, permitindo cadastro de usuários, gerenciamento de carros e controle de aluguéis diretamente pelo Discord.

🎯 Objetivo do Projeto

Projeto educacional com o objetivo de praticar:

🧠 Lógica de programação

🗂️ Estruturas de dados

🐍 Python aplicado

🔗 Desenvolvimento de APIs/bots com Discord

💾 Persistência de dados com arquivos JSON

🔐 Validações de dados (email, senha, permissões)

🛠️ Tecnologias Utilizadas

Python 3

discord.py

JSON (armazenamento de dados)

Regex (re) para validações

Discord UI (Buttons & Views)

📂 Estrutura de Dados

Os dados são armazenados no arquivo:

dados_carros.json


Contendo:

👤 Cadastros de administradores e clientes

🚗 Lista de carros

📊 Status de aluguel e manutenção

O arquivo é criado automaticamente caso não exista.

🚗 Funcionalidades
👤 Cadastro

Cadastro de clientes, funcionários e administradores

Validação de:

📧 Email

🔐 Senha forte (mín. 8 caracteres, maiúscula, minúscula, número e símbolo)

Prevenção de cadastros duplicados

🚘 Carros

Listar carros disponíveis

Adicionar e remover carros (admin)

Colocar carro em manutenção

Retirar carro da manutenção

📄 Aluguel

Alugar carro por número de dias

Cálculo automático do valor total

Devolver carro alugado

📋 Administração

Listar cadastros

Remover cadastros

Controle de permissões por email e senha do administrador

💬 Comandos Principais
📌 Cadastro
!cadastrar
!cadastrar_cliente NOME EMAIL SENHA
!cadastrar_adm NOME EMAIL SENHA

🚗 Carros
!listar_carros
!adicionar_carro MODELO ANO DIARIA EMAIL_ADMIN SENHA_ADMIN
!remover_carro ID EMAIL_ADMIN SENHA_ADMIN

🔧 Manutenção
!manutencao_on ID EMAIL_ADMIN SENHA_ADMIN
!manutencao_off ID EMAIL_ADMIN SENHA_ADMIN

📦 Aluguel
!alugar EMAIL_CLIENTE ID_CARRO DIAS
!devolver ID_CARRO

📋 Cadastros
!listar_cadastros
!remover_cadastro TIPO EMAIL

▶️ Como Executar

Clone o repositório:

git clone https://github.com/lucaszbrz/seu-repositorio.git


Instale as dependências:

pip install discord.py


Configure o token do bot:

TOKEN = "SEU_TOKEN_DO_DISCORD"


⚠️ Nunca suba seu token real para o GitHub.

Execute o projeto:

python bot.py

⚠️ Observações Importantes

Projeto com foco educacional

Dados armazenados localmente em JSON

Não recomendado para produção

Ideal para estudo de bots, lógica e estruturas de dados

🚀 Próximas Melhorias (Ideias)

🔒 Hash de senhas

🗄️ Banco de dados (SQLite / PostgreSQL)

📊 Relatórios de aluguel

🌐 Integração com API externa

🧪 Testes automatizados

👨‍💻 Autor

Lucas
🎓 Estudante de Análise e Desenvolvimento de Sistemas – FAESA
🐍 Python | ☕ Java | 🧠 Estruturas de Dados
🔗 GitHub: github.com/lucaszbrz
