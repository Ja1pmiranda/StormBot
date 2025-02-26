import discord
from discord import app_commands
from discord.ui import Select, View, Button
import json
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

token = os.getenv("STORM_TOKEN")
id_do_servidor = int(os.getenv("ID_STORM"))

# Carregar dados do JSON
with open(r"./dados/dados.json", "r", encoding="utf-8") as file:
    dados = json.load(file)

niveis = dados["niveis"]
PARTICIPANTES1 = dados["nomes_europa"]
PARTICIPANTES2 = dados["nomes_oeste_asia"]
PARTICIPANTES3 = dados["nomes_leste_asia"]
PARTICIPANTES4 = dados["nomes_africa/oceania"]

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

## -------------------------------------------------- POSTAR MISSÃO --------------------------------------------------

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

class ParticipanteDropdown(Select):
    def __init__(self, participantes, placeholder, embed: discord.Embed, field_name: str):
        self.embed = embed
        self.field_name = field_name
        options = [discord.SelectOption(label=p) for p in participantes]
        super().__init__(placeholder=placeholder, min_values=1, max_values=len(participantes), options=options)

    async def callback(self, interaction: discord.Interaction):
        novos_participantes = set(self.values)

        # Recupera os participantes atuais
        for field in self.embed.fields:
            if field.name == self.field_name:
                participantes_atuais = set(field.value.split(", ")) if field.value != "Nenhum participante ainda." else set()
                participantes_atualizados = participantes_atuais.symmetric_difference(novos_participantes)
                participantes_str = ", ".join(sorted(participantes_atualizados)) if participantes_atualizados else "Nenhum participante ainda."
                self.embed.set_field_at(
                    self.embed.fields.index(field),
                    name=self.field_name,
                    value=participantes_str,
                    inline=False
                )
                break

        await interaction.response.edit_message(embed=self.embed)


class MissaoView(View):
    def __init__(self, embed: discord.Embed):
        super().__init__()
        self.embed = embed
        # Usar custom_id exclusivo
        self.add_item(Button(label="Aceitar", style=discord.ButtonStyle.primary, custom_id="aceitar_1_missao"))

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.primary, custom_id="aceitar_1_missao")
    async def aceitar_callback(self, button: Button, interaction: discord.Interaction):
        dropdown_view = EditarParticipantesView(self.embed)
        await interaction.response.edit_message(embed=self.embed, view=dropdown_view)


class EditarParticipantesView(View):
    def __init__(self, embed: discord.Embed):
        super().__init__()
        self.embed = embed
        # Adicionar custom_ids exclusivos para cada botão
        self.add_item(ParticipanteDropdown(PARTICIPANTES1, "Europa", embed, "Participantes"))
        self.add_item(ParticipanteDropdown(PARTICIPANTES2, "Oeste da Ásia", embed, "Participantes"))
        self.add_item(ParticipanteDropdown(PARTICIPANTES3, "Leste da Ásia", embed, "Participantes"))
        self.add_item(ParticipanteDropdown(PARTICIPANTES4, "África/Oceania", embed, "Participantes"))
        self.add_item(Button(label="Confirmar", style=discord.ButtonStyle.success, custom_id="confirmar_1_editar"))

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success, custom_id="confirmar_1_editar")
    async def confirmar_callback(self, button: Button, interaction: discord.Interaction):
        confirmar_view = ConfirmarView(self.embed)
        await interaction.response.edit_message(embed=self.embed, view=confirmar_view)


class ConfirmarView(View):
    def __init__(self, embed: discord.Embed):
        super().__init__()
        self.embed = embed
        # Custom_id exclusivo para o botão
        self.add_item(Button(label="Editar", style=discord.ButtonStyle.secondary, custom_id="editar_1_confirmar"))

    @discord.ui.button(label="Editar", style=discord.ButtonStyle.secondary, custom_id="editar_1_confirmar")
    async def editar_callback(self, button: Button, interaction: discord.Interaction):
        editar_view = EditarParticipantesView(self.embed)
        await interaction.response.edit_message(embed=self.embed, view=editar_view)


async def criar_missao(interaction: discord.Interaction, nome: str, descricao: str, duracao: str, categorias: str, obs: str):
    embed = discord.Embed(title=f"**{nome.upper()}**")
    nome_do_canal = interaction.channel.name.lower()

    cores_por_nivel = {
        "principiante": discord.Color.from_str('#8B4513'),
        "avançado": discord.Color.from_str('#FFD700'),
        "santo": discord.Color.from_str('#00FF00'),
        "real": discord.Color.from_str('#00BFFF'),
        "imperial": discord.Color.from_str('#FF0000'),
        "divino": discord.Color.from_str('#000000'),
        "cosmico": discord.Color.from_str('#FFFFFF')
    }

    embed.color = cores_por_nivel.get(nome_do_canal, discord.Color.default())
    embed.add_field(name="Descrição", value=descricao, inline=False)
    embed.add_field(name="Duração", value=duracao, inline=True)
    embed.add_field(name="Categorias", value=categorias, inline=False)
    embed.add_field(name="Observações", value=obs, inline=True)
    embed.add_field(name="Participantes", value="Nenhum participante ainda.", inline=False)

    view = MissaoView(embed)
    await interaction.response.send_message(embed=embed, view=view)


client.run(token)
