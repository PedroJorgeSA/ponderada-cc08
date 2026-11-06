# Ponderada CC08 — Pedro Jorge Alves Soares

Análise de arquitetura, pipeline, threads, semáforos e deadlock da pulseira sensorial Tato, com a decisão de CTO.

O documento da entrega está em [`ponderada/ponderada-tato.md`](ponderada/ponderada-tato.md).

## Como rodar a questão A4

Requisito: Python 3.8 ou mais novo (só biblioteca padrão). A partir da raiz do repositório:

| Versão | Comando | O que mostra |
|---|---|---|
| 1 — sem sincronização | `python3 ponderada/codigo/versao1.py` | condição de corrida: amostras perdidas e duplicadas (às vezes travamento) |
| 2 — com semáforos | `python3 ponderada/codigo/versao2.py` | buffer correto com `vazio`, `cheio` e `mutex` |
| 3 — ordem trocada | `python3 ponderada/codigo/versao3.py` | deadlock por `wait(mutex)` antes de `wait(vazio)` |

Cada comando faz 3 execuções com 20.000 amostras e buffer de N = 4 posições e imprime a tabela de resultados.

Duração aproximada: menos de 1 s por execução nas versões 1 e 2; cerca de 1 s em cada execução da versão 3, que trava e é encerrada pelo timeout.
