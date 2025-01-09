import discord
from discord import app_commands
import json
from discord.ui import Button, View, Select
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

token = os.getenv("STORM_TOKEN")
id_do_servidor = int(os.getenv("ID_STORM"))
mural_id = int(os.getenv("ID_MURAL"))

# Carregar dados do JSON
with open(r"./dados/dados.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

niveis = dados["niveis"]
PARTICIPANTES = dados["nomes"]

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Bot conectado como {self.user}")

client = MyClient()
##--------------------------------------------------POSTAR MISSÃO----------------------------------------------------

@client.tree.command(guild=discord.Object(id=id_do_servidor), name="postar_missao", description="Postar uma nova missão.")
@app_commands.describe(
    nome="Nome da missão",
    descricao="Descrição da missão",
    duracao="Duração da missão",
    categorias="Categorias da missão",
    obs="Observações adicionais"
)
async def postar_missao(interaction: discord.Interaction, nome: str, descricao: str, duracao: str, categorias: str, obs: str):
    await criar_missao(interaction, nome, descricao, duracao, categorias, obs)

async def criar_missao(interaction: discord.Interaction, nome: str, descricao: str, duracao: str, categorias: str, obs: str):
    embed = discord.Embed(title=f" **{nome.upper()}**", color=discord.Color.red())
    embed.add_field(name="Descrição", value=descricao, inline=False)
    embed.add_field(name="Duração", value=duracao, inline=True)
    embed.add_field(name="Categorias", value=categorias, inline=False)
    embed.add_field(name="Observações", value=obs, inline=True)
    embed.add_field(name="Participantes", value="Nenhum participante ainda.", inline=False)

    accept_button = Button(label="Aceitar", style=discord.ButtonStyle.green)

    async def accept_callback(interaction: discord.Interaction):
        await selecionar_participantes(interaction, nome, embed, interaction.message)

    accept_button.callback = accept_callback

    view = View()
    view.add_item(accept_button)

    await interaction.response.send_message(embed=embed, view=view)

async def selecionar_participantes(interaction: discord.Interaction, nome: str, embed: discord.Embed, original_message: discord.Message):
    select_menu = Select(
        placeholder="Selecione os participantes",
        options=[discord.SelectOption(label=nome, value=nome) for nome in PARTICIPANTES],
        min_values=1,  # Número mínimo de seleções
        max_values=len(PARTICIPANTES)  # Número máximo de seleções
    )

    async def select_callback(interaction: discord.Interaction):
        # Defere a interação imediatamente
        await interaction.response.defer(ephemeral=True)

        selecionados = select_menu.values
        participantes_str = ", ".join(selecionados)

        # Atualizar o embed com os participantes selecionados
        embed.set_field_at(index=4, name="Participantes", value=participantes_str, inline=False)
        embed.color = discord.Color.gold()

        # Criar botão "Concluir"
        concluir_button = Button(label="Concluir", style=discord.ButtonStyle.blurple)

        # Mandar mensagem no mural
        mural = interaction.guild.get_channel(mural_id)
        if mural: #verifica se o canal mural existe
            link_missao = original_message.jump_url
            await mural.send(
                content=f"A missão **{nome.upper()}** foi aceita por\n"
                f"**{participantes_str}**\n"
                f"Confira os detalhes aqui: [{nome.upper()}]({link_missao})"
            )
            await mural.send(embed=embed)
        else:
            await interaction.response.send_message(
                content="Erro: O canal Mural não foi encontrado.",
                ephemeral=True
            )

        async def concluir_callback(interaction: discord.Interaction):
            link_missao = original_message.jump_url
            embed.color = discord.Color.green()
            await original_message.edit(embed=embed, view=None)

            await interaction.response.send_message(
                content=f"**Missão concluída**🎉:\n"
                f"[{nome.upper()}]({link_missao})\n"
                f"**Participantes:**\n"
                f"{participantes_str}",
                ephemeral=False
            )
            
            
            if mural: #verifica se o canal mural existe
                
                await mural.send(
                    content=f"🎯 **Missão concluída!**\n"
                    f"**Missão:** [{nome.upper()}]({link_missao})\n"
                    f"**Participantes:** {participantes_str}\n"
                )
                await mural.send(embed=embed)
            else:
                await interaction.response.send_message(
                    content="Erro: O canal Mural não foi encontrado.",
                    ephemeral=True
                )
            

        concluir_button.callback = concluir_callback

        # Atualizar o View para manter o Select e adicionar o botão "Concluir"
        view = View()
        view.add_item(select_menu)  # Adiciona o Select novamente
        view.add_item(concluir_button)  # Adiciona o botão "Concluir"

        # Atualizar a mensagem original com o novo View
        await original_message.edit(embed=embed, view=view)

    select_menu.callback = select_callback

    # Atualizar a mensagem original com o Select
    view = View()
    view.add_item(select_menu)

    # Defere a interação inicial
    await interaction.response.defer()

    await original_message.edit(view=view)



client.run(token)
