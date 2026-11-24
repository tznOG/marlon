from discord import app_commands
from .runtime import bot

grp_recompensa = app_commands.Group(
    name="recompensa", description="Comandos de recompensas"
)

grp_criar = app_commands.Group(name="criar", description="Criar itens no sistema")

grp_dar = app_commands.Group(name="dar", description="Dar itens para membros")

grp_remover = app_commands.Group(name="remover", description="Remover itens de membros")

grp_emblema = app_commands.Group(name="emblema", description="Gerenciar emblemas")

grp_codigo = app_commands.Group(name="codigo", description="Gerenciar códigos")

grp_loja = app_commands.Group(name="loja", description="Sistema de loja")

grp_destaque = app_commands.Group(
    name="destaque", description="Gerenciar destaques do perfil"
)

grp_economia = app_commands.Group(name="economia", description="Jogos e transferências")


bot.tree.add_command(grp_recompensa)
bot.tree.add_command(grp_criar)
bot.tree.add_command(grp_dar)
bot.tree.add_command(grp_remover)
bot.tree.add_command(grp_emblema)
bot.tree.add_command(grp_codigo)
bot.tree.add_command(grp_loja)
bot.tree.add_command(grp_destaque)
bot.tree.add_command(grp_economia)
