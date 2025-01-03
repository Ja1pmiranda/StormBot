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

# Carregar dados do JSON
json_path = os.path.join("dados","dados.json")
with open(json_path, "r") as f:
    dados = json.load(f)

VALID_NIVEIS = dados["niveis"]
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

@client.tree.command(guild=discord.Object(id=id_do_servidor), name="postar_missao", description="Postar uma nova missão.")
@app_commands.describe(nome="Nome da missão", descricao="Descrição da missão", duracao="Duração da missão")
async def postar_missao(interaction: discord.Interaction, nome: str, descricao: str, duracao: str):
    # Dropdown para selecionar o nível da missão
    nivel_select = Select(
        placeholder="Selecione o nível da missão",
        options=[discord.SelectOption(label=nivel, value=nivel) for nivel in VALID_NIVEIS]
    )

    async def nivel_callback(interaction: discord.Interaction):
        nivel = nivel_select.values[0]  # Captura o nível selecionado
        await criar_missao(interaction, nome, nivel, descricao, duracao)

    nivel_select.callback = nivel_callback

    view = View()
    view.add_item(nivel_select)

    await interaction.response.send_message(
        "Escolha o nível da missão no dropdown:",
        view=view,
        ephemeral=True
    )


async def criar_missao(interaction: discord.Interaction, nome: str, nivel: str, descricao: str, duracao: str):
    embed = discord.Embed(title=f"Missão: {nome}", color=discord.Color.blue())
    embed.add_field(name="Nível", value=nivel, inline=True)
    embed.add_field(name="Descrição", value=descricao, inline=False)
    embed.add_field(name="Duração", value=duracao, inline=True)
    embed.add_field(name="Participantes", value="Nenhum participante ainda.", inline=False)
    embed.set_footer(text="Use o botão 'Aceitar' para participar da missão!")

    accept_button = Button(label="Aceitar", style=discord.ButtonStyle.green)

    async def accept_callback(interaction: discord.Interaction):
        modal = AddParticipantsAutocomplete(embed_message=interaction.message)
        await interaction.response.send_modal(modal)

    accept_button.callback = accept_callback

    view = View()
    view.add_item(accept_button)

    await interaction.response.send_message(embed=embed, view=view)


class AddParticipantsAutocomplete(discord.ui.Modal):
    def __init__(self, embed_message: discord.Message):
        super().__init__(title="Adicionar Participantes")
        self.embed_message = embed_message

        self.participant_name = discord.ui.TextInput(
            label="Nome do Participante",
            placeholder="Digite para buscar...",
            required=True
        )
        self.add_item(self.participant_name)

    async def on_submit(self, interaction: discord.Interaction):
        new_participant = self.participant_name.value.strip()
        if new_participant not in PARTICIPANTES:
            await interaction.response.send_message(
                content=f"O participante `{new_participant}` não está na lista de permitidos.",
                ephemeral=True
            )
            return

        embed = self.embed_message.embeds[0]
        current_participants = embed.fields[-1].value

        if current_participants == "Nenhum participante ainda.":
            updated_participants = new_participant
        else:
            updated_participants = f"{current_participants}, {new_participant}"

        embed.set_field_at(
            index=3,
            name="Participantes",
            value=updated_participants,
            inline=False
        )

        conclude_button = Button(label="Concluir", style=discord.ButtonStyle.red)

        async def conclude_callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                content=f"A missão **{embed.title}** foi concluída com sucesso! 🎉",
                ephemeral=False
            )
            await self.embed_message.edit(view=None)

        conclude_button.callback = conclude_callback

        view = View()
        view.add_item(conclude_button)

        await self.embed_message.edit(embed=embed, view=view)
        await interaction.response.send_message(
            content=f"Participante `{new_participant}` adicionado à missão.",
            ephemeral=True
        )


client.run(token)
