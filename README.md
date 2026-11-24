# Marlon

Bot de economia virtual e emblemas colecionáveis para Discord. Reúne perfis, loja, recompensas e ferramentas para organizar atividades de uma comunidade.

O projeto roda em um homelab. Esta versão organiza o código em módulos e documenta os 30 comandos existentes. O banco usado pela comunidade e as credenciais não fazem parte do repositório.

## O que ele faz

- **Perfis e coleção:** saldo, bio, inventário paginado e até três emblemas em destaque.
- **Emblemas:** catálogo, detalhes, distribuição e resgate por códigos com limite de uso e validade.
- **Economia:** recompensa de 50 a 200 moedas a cada 24 horas, trabalho de 10 a 50 moedas a cada hora, transferências, cara ou coroa e slots. As moedas são internas ao bot, sem integração de pagamento.
- **Loja e ranking:** compra de emblemas por botões e rankings de moedas ou quantidade de emblemas.
- **Administração:** gestão de emblemas, códigos e saldos; anúncios de códigos e sessões de cinema; envio de embeds a partir de JSON do Discohook.
- **Chat:** respostas a menções e mensagens diretas usando a API da Groq. Essa parte depende de uma chave própria; a economia usa SQLite local.

## Usando no Discord

| Comando | O que aparece ou acontece |
| --- | --- |
| `/perfil` | Perfil com saldo, bio e emblemas em destaque. |
| `/loja ver` | Emblemas disponíveis, com botões para comprar usando moedas do bot. |
| `/recompensa diaria` | Recebe a recompensa do dia ou informa o tempo restante. |
| `/emblemas` | Abre a coleção com navegação entre páginas. |
| `/destaque definir emblemas:Participante, Cinéfilo` | Seleciona emblemas já possuídos para mostrar no perfil. |
| `/economia transferir usuario:@colega valor:25` | Transfere 25 moedas para outra pessoa. |

Os nomes de emblemas e o destinatário acima são exemplos. A lista completa, incluindo parâmetros e comandos administrativos, está em [Comandos](docs/COMANDOS.md).

Para uma apresentação curta, comece pelo perfil, abra a loja e termine na coleção de emblemas. Esse percurso mostra os comandos, os componentes interativos e a persistência dos dados. O [roteiro de capturas](docs/DEMONSTRACAO.md) orienta a preparação das imagens reais para este README.

## Tecnologias

Python, discord.py, SQLite e requests. A interface usa slash commands, embeds, botões, menus de seleção e modais do Discord. A chamada HTTP do chat executa em uma thread para não bloquear o loop de eventos enquanto aguarda a API.

## Executar localmente

Use Python 3.11 ou superior. Os testes desta preparação foram executados com Python 3.14; a CI também verifica outras versões.

```bash
git clone https://github.com/tznOG/marlon.git
cd marlon
python -m venv .venv
```

Ative o ambiente:

```bash
# Linux/macOS
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha os valores localmente. Não coloque credenciais em comandos do Git ou em issues.

| Variável | Uso |
| --- | --- |
| `DISCORD_TOKEN` | Token da aplicação de bot; necessário para conectar ao Discord. |
| `GROQ_API_KEY` | Chave para respostas de chat. |
| `MOEDA_EMOJI` | Emoji da moeda; o padrão é `💰`. Também aceita um emoji personalizado do seu servidor. |
| `ID_CARGO_MEMBRO` | Cargo mencionado nos anúncios que usam essa opção. |
| `ID_CANAL_LOGS` | Canal destinado aos erros; mantenha-o restrito à administração. |
| `DATABASE_PATH` | Caminho do SQLite. O padrão continua sendo `emblemas.db` no diretório de execução. |

No [Discord Developer Portal](https://discord.com/developers/applications), crie uma aplicação, adicione o bot e habilite **Message Content Intent** para as respostas por menção/DM. Convide-o com os escopos `bot` e `applications.commands`, concedendo as permissões de visualizar canais, enviar mensagens e inserir links/embeds nos canais necessários. Menções de cargos dependem das permissões e configurações desse cargo.

```bash
python -m marlon
# O ponto de entrada anterior também funciona:
python bot.py
```

Na primeira execução, as tabelas são criadas no SQLite. Ao conectar, o bot sincroniza os comandos com o Discord. Use um servidor de teste e um banco novo para experimentar; não execute duas instâncias sobre os mesmos dados.

## Organização

```text
marlon/
  config.py             Configuração por ambiente
  runtime.py            Instância do bot e intents
  database.py           Inicialização e conexão SQLite
  groups.py             Grupos dos slash commands
  helpers.py            Formatação e autocompletes
  views.py              Botões, menus, paginação e modal JSON
  chat.py               Integração HTTP com a Groq
  events.py             Eventos e tratamento de erros
  commands/
    community.py        Perfis, coleção, resgate e destaques
    economy.py          Recompensas, jogos e transferências
    shop.py             Loja
    admin.py            Gestão e anúncios
tests/                  Testes locais com dados sintéticos
docs/                   Comandos, arquitetura e decisões de revisão
```

Veja [Arquitetura e dados](docs/ARQUITETURA.md) para entender o fluxo e as escolhas do projeto.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes usam SQLite temporário e interações simuladas. Não conectam o bot ao Discord, não enviam mensagens e não chamam a Groq. Cobrem registro dos comandos, recompensas, transferências e resgate de emblemas. Isso não substitui o ensaio da interface em um servidor de teste.

## Estado desta revisão

A branch `main` preserva os corpos das funções e classes do bot original, com a conexão SQLite centralizada. Configuração saiu do código, a inicialização foi isolada e as dependências foram fixadas nas versões testadas localmente. As alterações e os limites dessa comparação estão em [Revisão](docs/REVISAO.md).

Correções que alteram comportamento ficam na branch `security/hardening`, para revisão separada. **Esta base preservada não deve ser tratada como uma versão com todos os ajustes de segurança já aplicados.** O bot em produção não foi alterado por esta preparação.

O modelo de dados representa uma comunidade por instância: não há separação por servidor Discord. As consultas SQLite são síncronas e a loja tem até 25 botões por mensagem. Esses limites estão documentados como próximos pontos de evolução, sem prometer suporte que ainda não foi implementado.

## Privacidade

O SQLite guarda IDs de usuários, saldos, bio, horários de recompensa e inventário. O chat envia o texto da mensagem e a instrução de personalidade para a Groq; ele não consulta o banco para compor a resposta. Mensagens e erros podem aparecer nos logs da versão original. Revise as propostas de proteção antes de habilitar o chat para outras pessoas.

Não há licença de redistribuição definida nesta revisão privada. Imagens do servidor, banco real e credenciais foram deixados fora do repositório.
