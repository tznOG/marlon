# Revisão para o repositório

## Reorganização preservando comportamento

A base veio de um único `bot.py`. Foram distribuídas 48 definições de funções e classes entre módulos. A comparação de AST confirmou os mesmos corpos e decoradores, permitindo apenas a substituição mecânica de `sqlite3.connect('emblemas.db')` pela função central `connect()`.

Isso preserva os 30 nomes de comandos, suas respostas, cálculos e regras existentes. Não é uma prova de equivalência de todas as condições de execução; os testes locais complementam a comparação.

Alterações de preparação identificadas:

- Token, chave e IDs saíram do código para variáveis de ambiente. Para reproduzir o ambiente antigo, configure os mesmos valores localmente; eles não são distribuídos no repositório.
- Sem configuração, o emoji padrão é genérico e os IDs opcionais são zero. Essas são opções de instalação, não uma migração dos dados reais.
- `main()` concentra a inicialização. Importar os módulos não cria o banco nem conecta ao Discord.
- Dependências diretas foram fixadas nas versões testadas em ambiente local. Não foi conferida equivalência de todas as dependências com o processo em produção.
- Não havia histórico Git no diretório original. O repositório começa nesta preparação, sem commits históricos inventados.

O banco da comunidade não foi copiado, consultado ou migrado. Nenhuma mudança foi aplicada ao serviço em produção.

## Ajustes de comportamento: revisão separada

A branch `security/hardening` contém propostas de proteção separadas da refatoração. Não confundir uma proposta no GitHub com uma correção já instalada no homelab.

Pontos encontrados no código original:

1. Credenciais estavam em literais. Elas foram removidas antes do primeiro commit; a rotação das credenciais existentes ainda precisa ser feita pelo responsável pelo bot.
2. Os comandos administrativos tinham `default_permissions`, sem uma verificação local correspondente. A [documentação do discord.py](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.default_permissions) diferencia a permissão padrão dos checks executados pelo bot. A proposta adiciona checks explícitos.
3. A requisição à Groq não tinha timeout e retornava corpo de erro ao usuário. Também havia log do conteúdo da mensagem em caso de falha.
4. Botões de compra usavam o preço guardado na criação da view, sem revalidar preço e disponibilidade no clique.
5. A paginação não restringia quem podia usar os botões; a listagem administrativa de códigos era pública no canal.

Nenhum desses pontos foi explorado contra a comunidade real. Os testes usam identidades e bancos sintéticos.

## Limites conhecidos mantidos nesta base

- Um banco global por instância, sem isolamento por servidor.
- Operações administrativas em lote podem atingir todos os usuários registrados quando o usuário-alvo fica vazio. Essa regra foi preservada e precisa de atenção na operação.
- Validações de quantidade, tamanho de embeds e consistência do inventário ainda merecem testes mais amplos.
- A loja exibe os itens, mas oferece no máximo 25 botões por view.
- Não há teste de carga, auditoria integral do homelab ou ensaio desta versão conectado ao Discord.

Esses limites devem orientar a próxima revisão; não foram escondidos para apresentar o projeto.
