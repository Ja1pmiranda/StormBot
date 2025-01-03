import discord
from discord import app_commands
import json
from discord.ui import Button, View
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

token = os.getenv("STORM_TOKEN")
id_do_servidor = int(os.getenv("ID_STORM"))

# Carregar dados do JSON
json_path = os.path.join("dados", "dados.json")
with open(json_path, "r") as f:
    dados = json.load(f)

# Criar um dicionário com os nomes e os user_ids
NOMES_E_IDS = {p["nome"]: int(p["user_id"]) for p in dados["nomes"]}

# Criar um dicionário com os grupos e os seus membros
GRUPOS_E_IDS = {grupo: [int(membro["user_id"]) for membro in membros] 
                for grupo, membros in dados["grupos"].items()}

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
    await criar_missao(interaction, nome, descricao, duracao)


async def criar_missao(interaction: discord.Interaction, nome: str, descricao: str, duracao: str):
    embed = discord.Embed(title=f"Missão: {nome}", color=discord.Color.blue())
    embed.add_field(name="Descrição", value=descricao, inline=False)
    embed.add_field(name="Duração", value=duracao, inline=True)
    embed.add_field(name="Participantes", value="Nenhum participante ainda.", inline=False)
    embed.set_footer(text="Use o botão 'Aceitar' para participar da missão!")

    accept_button = Button(label="Aceitar", style=discord.ButtonStyle.green)

    async def accept_callback(interaction: discord.Interaction):
        # Enviar mensagem privada para os participantes (individuais e de grupo)
        participantes = await obter_participantes(interaction.message.embeds[0].fields[-1].value)
        
        for participante_id in participantes:
            try:
                user = await client.fetch_user(participante_id)  # Obtém o usuário a partir do ID
                await user.send(content=f"Você foi adicionado à missão **{nome}**! Boa sorte! 🎉")
            except discord.Forbidden:
                await interaction.response.send_message(
                    content="Não foi possível enviar uma mensagem privada para todos os participantes.",
                    ephemeral=True
                )

        modal = AddParticipantsModal(embed_message=interaction.message)
        await interaction.response.send_modal(modal)

    accept_button.callback = accept_callback

    view = View()
    view.add_item(accept_button)

    await interaction.response.send_message(embed=embed, view=view)


async def obter_participantes(participantes_str: str):
    participantes = []
    for participante in participantes_str.split(', '):
        if participante in NOMES_E_IDS:
            participantes.append(NOMES_E_IDS[participante])
        elif participante in GRUPOS_E_IDS:
            participantes.extend(GRUPOS_E_IDS[participante])
    return participantes


class AddParticipantsModal(discord.ui.Modal):
    def __init__(self, embed_message: discord.Message):
        super().__init__(title="Adicionar Participantes")
        self.embed_message = embed_message

        self.participant_name = discord.ui.TextInput(
            label="Nome do Participante ou Grupo",
            placeholder="Digite o nome ou grupo...",
            required=True
        )
        self.add_item(self.participant_name)

    async def on_submit(self, interaction: discord.Interaction):
        new_participant = self.participant_name.value.strip()

        participantes = []
        if new_participant in NOMES_E_IDS:
            participantes = [new_participant]
        elif new_participant in GRUPOS_E_IDS:
            participantes = GRUPOS_E_IDS[new_participant]
        else:
            await interaction.response.send_message(
                content=f"O participante ou grupo `{new_participant}` não está na lista de permitidos.",
                ephemeral=True
            )
            return

        embed = self.embed_message.embeds[0]
        current_participants = embed.fields[-1].value

        if current_participants == "Nenhum participante ainda.":
            updated_participants = ", ".join(participantes)
        else:
            updated_participants = f"{current_participants}, {', '.join(participantes)}"

        embed.set_field_at(
            index=4,
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
            content=f"Participante(s) `{new_participant}` adicionado(s) à missão.",
            ephemeral=True
        )


client.run(token)
