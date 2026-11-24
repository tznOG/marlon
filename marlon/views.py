import discord
import math
import json
from .config import MOEDA_EMOJI
from .database import connect, check_user_exists
from .runtime import bot
from .helpers import formatar_moeda


class JSONModal(discord.ui.Modal, title="Colar JSON do Discohook"):
    json_text = discord.ui.TextInput(
        label="Cole o JSON aqui",
        style=discord.TextStyle.paragraph,
        placeholder='{"content": "...", "embeds": [...]}',
        required=True,
        max_length=4000,
    )

    def __init__(self, canal_alvo):
        super().__init__()
        self.canal_alvo = canal_alvo

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data = json.loads(self.json_text.value)
            content = data.get("content", None)
            embeds_list = []
            if "embeds" in data:
                for embed_data in data["embeds"]:
                    embeds_list.append(discord.Embed.from_dict(embed_data))

            if self.canal_alvo:
                await self.canal_alvo.send(content=content, embeds=embeds_list)
                await interaction.response.send_message(
                    f"✅ Mensagem enviada para {self.canal_alvo.mention}!",
                    ephemeral=True,
                )
            else:
                await interaction.channel.send(content=content, embeds=embeds_list)
                await interaction.response.send_message(
                    "✅ Mensagem enviada!", ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro no JSON: {e}", ephemeral=True
            )


class ProfilePaginationView(discord.ui.View):
    def __init__(
        self,
        full_inventory,
        user,
        saldo,
        bio,
        destaques_visual,
        interaction,
        items_per_page=10,
    ):
        super().__init__(timeout=60)
        self.full_inventory = full_inventory
        self.user = user
        self.saldo = saldo
        self.bio = bio
        self.destaques_visual = destaques_visual
        self.interaction = interaction
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = (
            math.ceil(len(full_inventory) / items_per_page) if full_inventory else 1
        )
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page >= self.total_pages - 1
        if not self.full_inventory or self.total_pages <= 1:
            self.children[0].disabled = True
            self.children[1].disabled = True

    async def on_timeout(self):
        self.clear_items()
        try:
            await self.interaction.edit_original_response(view=None)
        except:
            pass

    def create_embed(self):
        embed = discord.Embed(
            title=f"Perfil de {self.user.display_name}", color=0x2B2D31
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.add_field(name="Bio", value=self.bio, inline=False)
        valor_formatado = formatar_moeda(self.saldo)
        embed.add_field(
            name="\u200b",
            value=f"{MOEDA_EMOJI} **Moedas:** {valor_formatado}\n\u200b",
            inline=False,
        )
        if self.destaques_visual:
            embed.add_field(
                name="Emblemas em destaque",
                value=self.destaques_visual + "\n\u200b",
                inline=False,
            )
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.full_inventory[start:end]
        lista_str = (
            "\n".join(page_items) if page_items else "Nenhum emblema na coleção."
        )
        embed.add_field(name="Coleção de Emblemas", value=lista_str, inline=False)
        embed.set_footer(
            text=f"{len(self.full_inventory)} Emblemas • Página {self.current_page + 1} de {self.total_pages}"
        )
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction, button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction, button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)


class GenericListView(discord.ui.View):
    def __init__(self, data, title, interaction, items_per_page=20):
        super().__init__(timeout=60)
        self.data = data
        self.title = title
        self.interaction = interaction
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = math.ceil(len(data) / items_per_page)
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page >= self.total_pages - 1

    async def on_timeout(self):
        self.clear_items()
        try:
            await self.interaction.edit_original_response(view=None)
        except:
            pass

    def create_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.data[start:end]
        desc = "\n".join(page_items) if page_items else "Nada encontrado."
        embed = discord.Embed(title=self.title, description=desc, color=0x2B2D31)
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(
            text=f"{len(self.data)} Emblemas • Página {self.current_page + 1} de {self.total_pages}"
        )
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction, button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction, button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)


class BuyButton(discord.ui.Button):
    def __init__(self, nome, preco, emoji):
        super().__init__(
            style=discord.ButtonStyle.success,
            label=f"{nome} ({preco})",
            emoji=emoji,
            custom_id=f"buy_{nome}",
        )
        self.nome_emblema = nome
        self.preco = preco

    async def callback(self, interaction: discord.Interaction):
        check_user_exists(interaction.user.id)
        conn = connect()
        c = conn.cursor()
        c.execute("SELECT saldo FROM usuarios WHERE user_id=?", (interaction.user.id,))
        saldo = c.fetchone()[0]
        c.execute(
            "SELECT 1 FROM inventario WHERE user_id=? AND emblema_nome=?",
            (interaction.user.id, self.nome_emblema),
        )
        if c.fetchone():
            await interaction.response.send_message(
                f"⚠️ Já possui **{self.nome_emblema}**.", ephemeral=True
            )
            conn.close()
            return
        if saldo < self.preco:
            await interaction.response.send_message(
                f"❌ Saldo insuficiente.", ephemeral=True
            )
            conn.close()
            return

        try:
            c.execute(
                "UPDATE usuarios SET saldo = saldo - ? WHERE user_id=?",
                (self.preco, interaction.user.id),
            )
            c.execute(
                "INSERT INTO inventario (user_id, emblema_nome) VALUES (?, ?)",
                (interaction.user.id, self.nome_emblema),
            )
            conn.commit()
            c.execute(
                "SELECT url_imagem FROM emblemas WHERE nome=?", (self.nome_emblema,)
            )
            url = c.fetchone()[0]
            embed = discord.Embed(
                title="Compra Realizada!",
                description=f"Comprou **{self.nome_emblema}**!",
                color=0x00FF00,
            )
            embed.set_thumbnail(url=url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erro: {e}", ephemeral=True)
        finally:
            conn.close()


class ShopView(discord.ui.View):
    def __init__(self, items):
        super().__init__(timeout=None)
        for item in items[:25]:
            self.add_item(BuyButton(nome=item[1], preco=item[2], emoji=item[0]))


class RankingSelect(discord.ui.Select):
    def __init__(self):
        try:
            moeda_emoji = discord.PartialEmoji.from_str(MOEDA_EMOJI)
        except:
            moeda_emoji = "💰"
        options = [
            discord.SelectOption(
                label="Moedas",
                value="moedas",
                description="Ver o ranking de moedas",
                emoji=moeda_emoji,
            ),
            discord.SelectOption(
                label="Emblemas",
                value="emblemas",
                description="Ver o ranking de emblemas",
                emoji="🏆",
            ),
        ]
        super().__init__(
            placeholder="Selecione o ranking...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        conn = connect()
        c = conn.cursor()
        embed = discord.Embed(color=0xFFD700)
        embed.set_thumbnail(url=bot.user.display_avatar.url)

        if self.values[0] == "moedas":
            embed.title = "💰 Ranking de Moedas"
            c.execute(
                "SELECT user_id, saldo FROM usuarios ORDER BY saldo DESC LIMIT 10"
            )
            dados = c.fetchall()
            if not dados:
                embed.description = "Nenhum dado encontrado."
            else:
                linhas = [
                    f"**{i}.** <@{uid}> • **{formatar_moeda(saldo)}** {MOEDA_EMOJI}"
                    for i, (uid, saldo) in enumerate(dados, 1)
                ]
                embed.description = "\n".join(linhas)

        elif self.values[0] == "emblemas":
            embed.title = "🏆 Ranking de Emblemas"
            c.execute(
                "SELECT user_id, COUNT(*) as qtd FROM inventario GROUP BY user_id ORDER BY qtd DESC LIMIT 10"
            )
            dados = c.fetchall()
            if not dados:
                embed.description = "Nenhum dado encontrado."
            else:
                linhas = [
                    f"**{i}.** <@{uid}> • **{qtd}** Emblemas"
                    for i, (uid, qtd) in enumerate(dados, 1)
                ]
                embed.description = "\n".join(linhas)

        conn.close()
        await interaction.response.edit_message(embed=embed)


class RankingView(discord.ui.View):
    def __init__(self, interaction):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.add_item(RankingSelect())

    async def on_timeout(self):
        self.clear_items()
        try:
            await self.interaction.edit_original_response(view=None)
        except:
            pass
