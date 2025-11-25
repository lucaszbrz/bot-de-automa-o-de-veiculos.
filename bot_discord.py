import discord
from discord.ext import commands
import json
import os
import re
from discord.ui import View, Button, Modal, TextInput
import discord
from discord.ext import commands

fluxos_cadastro = {}  # estado por usuário

# Se não tiver o arquivo de dados, cria uma estrutura inicial

def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

def validar_senha(senha):
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."

    if not re.search(r'[A-Z]', senha):
        return False, "A senha deve ter pelo menos uma letra MAIÚSCULA."

    if not re.search(r'[a-z]', senha):
        return False, "A senha deve ter pelo menos uma letra minúscula."

    if not re.search(r'[0-9]', senha):
        return False, "A senha deve ter pelo menos um número."

    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', senha):
        return False, "A senha deve ter pelo menos um caractere especial."

    return True, "Senha válida."

DATA_FILE = "dados_carros.json"
if not os.path.isfile(DATA_FILE):
    initial = {
        "cadastros": {
            "administrador": [],
            "cliente": []
        },
        "carros": [
            {"id": 1, "modelo": "Fiat Mobi", "ano": 2020, "diaria": 80.0, "disponivel": True, "manutencao": False},
            {"id": 2, "modelo": "Chevrolet Onix", "ano": 2021, "diaria": 100.0, "disponivel": True, "manutencao": False},
            {"id": 3, "modelo": "Volkswagen Gol", "ano": 2019, "diaria": 75.0, "disponivel": True, "manutencao": False},
            {"id": 4, "modelo": "Hyundai HB20", "ano": 2022, "diaria": 110.0, "disponivel": True, "manutencao": False},
        ]
    }
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(initial, f, indent=4)

# Funções para ler e salvar dados
def carregar_dados():
    with open(DATA_FILE, "r", encoding="utf8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(dados, f, indent=4)

# Funções de lógica (adaptadas)
def listar_carros_texto(dados, apenas_disponiveis=True):
    linhas = []
    for c in dados["carros"]:
        if apenas_disponiveis and (not c["disponivel"] or c.get("manutencao")):
            continue
        status = "Em manutenção" if c.get("manutencao") else ("Disponível" if c["disponivel"] else f"Alugado por {c.get('alugado_por')}")
        linhas.append(f"{c['id']}: {c['modelo']} ({c['ano']}) - R${c['diaria']:.2f}/dia - {status}")
    if not linhas:
        return "Nenhum carro encontrado."
    return "\n".join(linhas)

def encontrar_carro(dados, carro_id):
    for c in dados["carros"]:
        if c["id"] == carro_id:
            return c
    return None

# Setup do bot
intents = discord.Intents.default()
intents.message_content = True  # necessário para ler o conteúdo das mensagens e comandos

bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltou algum argumento! Verifique o formato correto do comando.")
    else:
        raise error

# Eventos
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    # Ignora mensagens do próprio bot
    if message.author == bot.user:
        return

    # Aqui você pode colocar lógica adicional se quiser reagir a mensagens genéricas

    # Importante: processar os comandos depois de fazer outras coisas
    await bot.process_commands(message)
 

# Comandos
class MenuCadastro(View):
    def __init__(self, autor_id):
        super().__init__(timeout=60)
        self.autor_id = autor_id

    async def interaction_check(self, interaction):
        return interaction.user.id == self.autor_id

    @discord.ui.button(label="Cadastrar Cliente", style=discord.ButtonStyle.green)
    async def cliente(self, interaction: discord.Interaction, button: Button):
        fluxos_cadastro[self.autor_id] = {"tipo": "cliente", "etapa": 1}
        await interaction.response.send_message("Digite o **nome do cliente**:", ephemeral=True)

    @discord.ui.button(label="Cadastrar Funcionário", style=discord.ButtonStyle.blurple)
    async def func(self, interaction: discord.Interaction, button: Button):
        fluxos_cadastro[self.autor_id] = {"tipo": "funcionario", "etapa": 1}
        await interaction.response.send_message("Digite o **nome do funcionário**:", ephemeral=True)

@bot.command()
async def cadastrar(ctx):
    await ctx.send("Selecione o tipo de cadastro:", view=MenuCadastro(ctx.author.id))
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    user_id = message.author.id
    if message.author.bot:
        return

    if user_id not in fluxos_cadastro:
        return

    fluxo = fluxos_cadastro[user_id]
    etapa = fluxo["etapa"]

    # ------- ETAPA 1 — NOME -------
    if etapa == 1:
        fluxo["nome"] = message.content.strip()
        fluxo["etapa"] = 2
        await message.channel.send("Agora digite o **email**:")
        return

    # ------- ETAPA 2 — EMAIL -------
    if etapa == 2:
        email = message.content.strip().lower()

        # valida email
        if "@" not in email or "." not in email:
            await message.channel.send("❌ Email inválido. Tente novamente.")
            return

        # verifica duplicados
        dados = carregar_dados()
        for categoria in dados["cadastros"].values():
            for pessoa in categoria:
                if pessoa["email"] == email:
                    await message.channel.send(
                        f"⚠ **ALERTA**: esse email já está cadastrado para **{pessoa['nome']}**!"
                    )
                    return

        fluxo["email"] = email
        fluxo["etapa"] = 3
        await message.channel.send("Digite a **senha** (mín: 8 caracteres, maiúscula, minúscula, número e símbolo):")
        return

    # ------- ETAPA 3 — SENHA -------
    if etapa == 3:
        senha = message.content.strip()

        import re
        forte = (len(senha) >= 8 and
                 re.search(r"[A-Z]", senha) and
                 re.search(r"[a-z]", senha) and
                 re.search(r"\d", senha) and
                 re.search(r"[!@#$%^&*()_+=\-]", senha))

        if not forte:
            await message.channel.send("❌ Senha fraca! Siga as regras e tente novamente.")
            return

        fluxo["senha"] = senha

        # FINALIZA CADASTRO
        dados = carregar_dados()
        tipo = fluxo["tipo"]

        dados["cadastros"][tipo].append({
            "nome": fluxo["nome"],
            "email": fluxo["email"],
            "senha": fluxo["senha"]
        })

        salvar_dados(dados)

        await message.channel.send(
            f"✅ **Cadastro concluído!**\n"
            f"Nome: {fluxo['nome']}\n"
            f"Email: {fluxo['email']}\n"
            f"Tipo: {tipo.capitalize()}"
        )

        del fluxos_cadastro[user_id]
class MenuEditar(View):
    def __init__(self, email):
        super().__init__(timeout=60)
        self.email = email

    @discord.ui.button(label="Editar Nome", style=discord.ButtonStyle.green)
    async def nome(self, inter, btn):
        await inter.response.send_message("Digite o novo nome:")

    @discord.ui.button(label="Editar Email", style=discord.ButtonStyle.blurple)
    async def email_btn(self, inter, btn):
        await inter.response.send_message("Digite o novo email:")

    @discord.ui.button(label="Editar Senha", style=discord.ButtonStyle.red)
    async def senha(self, inter, btn):
        await inter.response.send_message("Digite a nova senha:")
@bot.command()
async def editar(ctx, email: str):
    await ctx.send("Escolha o que deseja editar:", view=MenuEditar(email.lower()))

@bot.command(name="listar_carros")
async def cmd_listar_carros(ctx, apenas_disponiveis: str = "sim"):
    dados = carregar_dados()
    apenas_disp = apenas_disponiveis.lower() in ("sim", "s", "true", "verdadeiro")
    texto = listar_carros_texto(dados, apenas_disp)
    await ctx.send(f"```\n{texto}\n```")

@bot.command(name="cadastrar_adm")
async def cmd_cadastrar_adm(ctx, nome: str, email: str, senha: str):
    dados = carregar_dados()
    for adm in dados["cadastros"]["administrador"]:
        if adm["email"] == email.lower():
            await ctx.send("Email de administrador já cadastrado.")
            return
    dados["cadastros"]["administrador"].append({
        "nome": nome,
        "email": email.lower(),
        "senha": senha
    })
    salvar_dados(dados)
    await ctx.send("Administrador cadastrado com sucesso.")


@bot.command(name="cadastrar_cliente")
async def cmd_cadastrar_cliente(ctx, nome: str = None, email: str = None, senha: str = None):

    # Checar argumentos ausentes
    if nome is None or email is None or senha is None:
        await ctx.send("❌ Formato incorreto!\nUse: `!cadastrar_cliente NOME EMAIL SENHA`")
        return

    # Validação de email
    if not validar_email(email):
        await ctx.send("❌ Email inválido! Use algo como: exemplo@gmail.com")
        return

    # Validação de senha
    senha_ok, msg = validar_senha(senha)
    if not senha_ok:
        await ctx.send(f"❌ Senha inválida: {msg}")
        return

    dados = carregar_dados()

    for cli in dados["cadastros"]["cliente"]:
        if cli["email"] == email.lower():
            await ctx.send("❌ Esse email já está cadastrado.")
            return

    dados["cadastros"]["cliente"].append({
        "nome": nome,
        "email": email.lower(),
        "senha": senha
    })

    salvar_dados(dados)
    await ctx.send("✔️ Cliente cadastrado com sucesso!")


@bot.command(name="alugar")
async def cmd_alugar(ctx, cliente_email: str, carro_id: int, dias: int):
    dados = carregar_dados()
    carro = encontrar_carro(dados, carro_id)
    if not carro:
        await ctx.send("Carro não encontrado.")
        return
    if carro.get("manutencao"):
        await ctx.send("Carro em manutenção, não disponível para aluguel.")
        return
    if not carro["disponivel"]:
        await ctx.send("Carro indisponível para aluguel.")
        return

    cliente = next((c for c in dados["cadastros"]["cliente"] if c["email"] == cliente_email.lower()), None)
    if not cliente:
        await ctx.send("Cliente não cadastrado.")
        return
    if dias <= 0:
        await ctx.send("Número de dias inválido.")
        return

    valor_total = carro["diaria"] * dias
    carro["disponivel"] = False
    carro["alugado_por"] = cliente_email.lower()
    carro["dias"] = dias
    carro["valor_total"] = valor_total

    salvar_dados(dados)
    await ctx.send(f"Aluguel confirmado! Total: R${valor_total:.2f} por {dias} dias.")

@bot.command(name="devolver")
async def cmd_devolver(ctx, carro_id: int):
    dados = carregar_dados()
    carro = encontrar_carro(dados, carro_id)
    if not carro:
        await ctx.send("Carro não encontrado.")
        return
    if carro["disponivel"]:
        await ctx.send("Esse carro não está alugado.")
        return

    carro["disponivel"] = True
    carro.pop("alugado_por", None)
    carro.pop("dias", None)
    carro.pop("valor_total", None)
    salvar_dados(dados)
    await ctx.send(f"Carro **{carro['modelo']}** devolvido com sucesso.")

@bot.command(name="adicionar_carro")
async def cmd_adicionar_carro(ctx, modelo: str, ano: int, diaria: float, admin_email: str, admin_senha: str):
    dados = carregar_dados()
    adm = next((a for a in dados["cadastros"]["administrador"] if a["email"] == admin_email.lower() and a["senha"] == admin_senha), None)
    if not adm:
        await ctx.send("Administrador não autorizado.")
        return
    novos = dados["carros"]
    next_id = max([c["id"] for c in novos], default=0) + 1
    novos.append({
        "id": next_id,
        "modelo": modelo,
        "ano": ano,
        "diaria": diaria,
        "disponivel": True,
        "manutencao": False
    })
    salvar_dados(dados)
    await ctx.send(f"Carro {modelo} adicionado com ID {next_id}.")

@bot.command(name="manutencao_on")
async def cmd_manutencao_on(ctx, carro_id: int, admin_email: str, admin_senha: str):
    dados = carregar_dados()
    adm = next((a for a in dados["cadastros"]["administrador"] if a["email"] == admin_email.lower() and a["senha"] == admin_senha), None)
    if not adm:
        await ctx.send("Administrador não autorizado.")
        return
    carro = encontrar_carro(dados, carro_id)
    if not carro:
        await ctx.send("Carro não encontrado.")
        return
    if not carro["disponivel"]:
        await ctx.send("Carro alugado, não pode ir pra manutenção.")
        return
    carro["manutencao"] = True
    carro["disponivel"] = False
    salvar_dados(dados)
    await ctx.send(f"Carro **{carro['modelo']}** está agora em manutenção.")

@bot.command(name="manutencao_off")
async def cmd_manutencao_off(ctx, carro_id: int, admin_email: str, admin_senha: str):
    dados = carregar_dados()
    adm = next((a for a in dados["cadastros"]["administrador"] if a["email"] == admin_email.lower() and a["senha"] == admin_senha), None)
    if not adm:
        await ctx.send("Administrador não autorizado.")
        return
    carro = encontrar_carro(dados, carro_id)
    if not carro:
        await ctx.send("Carro não encontrado.")
        return
    if not carro.get("manutencao"):
        await ctx.send("Carro não está em manutenção.")
        return
    carro["manutencao"] = False
    carro["disponivel"] = True
    salvar_dados(dados)
    await ctx.send(f"Carro **{carro['modelo']}** saiu da manutenção e está disponível.")

@bot.command(name="remover_carro")
async def cmd_remover_carro(ctx, carro_id: int, admin_email: str, admin_senha: str):
    dados = carregar_dados()
    adm = next((a for a in dados["cadastros"]["administrador"] if a["email"] == admin_email.lower() and a["senha"] == admin_senha), None)
    if not adm:
        await ctx.send("Administrador não autorizado.")
        return
    carro = encontrar_carro(dados, carro_id)
    if not carro:
        await ctx.send("Carro não encontrado.")
        return
    if not carro["disponivel"] and not carro.get("manutencao"):
        await ctx.send("Carro está alugado, não pode remover.")
        return
    dados["carros"].remove(carro)
    salvar_dados(dados)
    await ctx.send(f"Carro **{carro['modelo']}** removido com sucesso.")

@bot.command(name="listar_cadastros")
async def cmd_listar_cadastros(ctx, tipo: str = None):
    dados = carregar_dados()
    cad = dados["cadastros"]
    if tipo:
        tipo = tipo.lower()
        if tipo not in cad:
            await ctx.send("Tipo inválido. Use `administrador` ou `cliente`.")
            return
        lista = cad[tipo]
        if not lista:
            await ctx.send(f"Nenhum {tipo} cadastrado.")
            return
        texto = "\n".join([f"{i+1}. {u['nome']} — {u['email']}" for i, u in enumerate(lista)])
        await ctx.send(f"Cadastros de **{tipo}**:\n{texto}")
    else:
        partes = []
        for t in cad:
            parte = f"**{t.capitalize()}s:**\n"
            parte += "\n".join([f"- {u['nome']} — {u['email']}" for u in cad[t]]) or "Nenhum"
            partes.append(parte)
        await ctx.send("\n".join(partes))
        
@bot.command(name="remover_cadastro")
async def cmd_remover_cadastro(ctx, tipo: str, email: str):
    tipo = tipo.lower()

    # Tipos permitidos
    tipos_validos = ["cliente", "gerente", "funcionario"]
    if tipo not in tipos_validos:
        await ctx.send(
            "❌ Tipo inválido! Use um destes:\n`cliente`, `gerente`, `funcionario`"
        )
        return

    dados = carregar_dados()
    lista = dados["cadastros"].get(tipo, [])

    # Procura o registro
    for item in lista:
        if item["email"] == email.lower():
            lista.remove(item)
            salvar_dados(dados)
            await ctx.send(f"✅ {tipo.capitalize()} removido com sucesso!")
            return

    # Se não encontrar
    await ctx.send(f"❌ Nenhum {tipo} com este email foi encontrado.")


# Para rodar o bot: (apenas para teste; NÃO comite este arquivo com o token)
TOKEN = "MTQzOTExNDUzNTQ0NDQxNDUwNQ.Gn72Yp.ZNEquiD14yAuyKHB90tMTURnr5TK5wGbT90Ggg"
bot.run(TOKEN)
print("TOKEN =", repr(TOKEN))  # deixe isso AQUI

