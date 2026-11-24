# Proposta de proteção — revisão separada

Esta branch muda comportamentos específicos da base preservada. Não foi aplicada ao homelab e não faz parte da promessa de refatoração sem mudanças funcionais.

| Situação | Base preservada | Proposta |
| --- | --- | --- |
| Comando administrativo | Permissão padrão declarada ao Discord. | Check de administrador no momento da execução. |
| Modal de anúncio | Usa a autorização da abertura. | Confere novamente a permissão ao enviar. |
| Listagem de códigos | Mensagem visível no canal. | Resposta privada ao administrador; nova checagem nos controles. |
| Paginação e ranking | Outra pessoa pode acionar os componentes. | Componentes limitados a quem abriu a view. |
| Botão antigo da loja | Usa preço e estado guardados na view. | Confere disponibilidade e preço atual; se mudou, pede para reabrir a loja sem cobrar. |
| Compra simultânea | Validações fora de uma transação explícita. | Validação, débito e inclusão no inventário dentro de `BEGIN IMMEDIATE`. |
| Groq sem chave | Faz requisição que tende a falhar. | Não chama o provedor e informa que o chat não está configurado. |
| Falha da Groq | Retorna corpo bruto do erro e pode registrar a mensagem do usuário. | Retorno genérico, timeout de conexão/leitura e log do tipo de falha, sem texto da conversa nesse caminho. |
| Menções geradas pelo chat | Resposta pode disparar menções. | Resposta usa `AllowedMentions.none()`. |

Nomes dos comandos, cálculo de moedas, intervalos de recompensas, texto de sucesso das compras, personalidade do chat e esquema SQLite permanecem os mesmos. Os testes da base continuam sendo executados.

## Antes de aplicar

Testar esta branch em um servidor Discord isolado, com conta de bot e SQLite de teste. Conferir permissões, interface, moeda e anúncios. Fazer backup do banco real antes de qualquer implantação. A rotação das credenciais antigas é uma tarefa operacional separada; não é feita por este PR.

## O que esta proposta não resolve

Não acrescenta isolamento entre servidores, limites de consumo da Groq, confirmação para operações administrativas em lote, migração completa das regras de inventário ou suporte a múltiplos processos. SQLite e algumas validações permanecem como na base. Os logs gerais de eventos e comandos também ainda precisam de uma revisão específica; a redução de logs aqui se limita ao caminho de conversa com a Groq.
