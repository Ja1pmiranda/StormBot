import discord
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from dotenv import load_dotenv
import os

load_dotenv()

# Acessa as variáveis
token = os.getenv("STORM_TOKEN")
id_do_servidor = os.getenv("ID_STORM")


class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True

        print(f"Entramos como {self.user}.")


aclient = client()
tree = app_commands.CommandTree(aclient)

# Comando de Postar Missão
@tree.command(guild=discord.Object(id=id_do_servidor), name="postar_missao", description="Postar uma nova missão")
async def postar_missao(interaction: discord.Interaction, nome: str, nivel: int, descricao: str, duracao: str):
    embed = discord.Embed(title=f"Missão: {nome}", color=discord.Color.blue())
    embed.add_field(name="Nível", value=nivel, inline=True)
    embed.add_field(name="Descrição", value=descricao, inline=False)
    embed.add_field(name="Duração", value=duracao, inline=True)
    embed.add_field(name="Participantes", value="Nenhum participante ainda.", inline=False)

    # Botão de Aceitar
    accept_button = Button(label="Aceitar", style=discord.ButtonStyle.green)

    async def accept_callback(interaction: discord.Interaction):
        modal = AddParticipantsModal(embed_message=interaction.message)
        await interaction.response.send_modal(modal)

    accept_button.callback = accept_callback

    view = View()
    view.add_item(accept_button)

    await interaction.response.send_message(embed=embed, view=view)


class AddParticipantsModal(Modal):
    def __init__(self, embed_message: discord.Message):
        super().__init__(title="Adicionar Participantes")
        self.embed_message = embed_message

        # Campo para inserir participantes
        self.participants = TextInput(
            label="Nomes dos participantes",
            placeholder="João, Mario, Maria, Andre",
            required=True
        )
        self.add_item(self.participants)

    async def on_submit(self, interaction: discord.Interaction):
        # Obter o embed original
        embed = self.embed_message.embeds[0]

        # Adicionar novos participantes
        new_participants = [name.strip() for name in self.participants.value.split(",")]
        current_participants = embed.fields[-1].value
        if current_participants == "Nenhum participante ainda.":
            updated_participants = "\n".join(new_participants)
        else:
            updated_participants = f"{current_participants}\n" + "\n".join(new_participants)

        # Atualizar o campo de participantes no embed
        embed.set_field_at(
            index=3,  # O índice do campo de "Participantes"
            name="Participantes",
            value=updated_participants,
            inline=False
        )

        # Criar botão de Concluir
        conclude_button = Button(label="Concluir", style=discord.ButtonStyle.red)

        async def conclude_callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                content=f"A missão **{embed.title}** foi concluída com sucesso! 🎉",
                ephemeral=True
            )
            await self.embed_message.edit(view=None)  # Remove os botões após concluir.

        conclude_button.callback = conclude_callback

        # Atualizar a mensagem original com o botão "Concluir"
        view = View()
        view.add_item(conclude_button)

        await self.embed_message.edit(embed=embed, view=view)

        # Confirmação de que os participantes foram adicionados
        await interaction.response.send_message(
            content=f"Participantes adicionados: {', '.join(new_participants)}",
            ephemeral=True
        )


aclient.run(token)