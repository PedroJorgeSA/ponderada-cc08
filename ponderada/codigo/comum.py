"""
comum.py - Funções compartilhadas pelas três versões da questão A4.

Ponderada CC08 - Pulseira Tato
Autor: Pedro Jorge Alves Soares

Contém os parâmetros do experimento (N, total de amostras, timeout),
a análise do que o consumidor recebeu (consumidas, perdidas, duplicadas)
e a rotina que roda uma versão várias vezes e imprime a tabela de resultados.
"""

import time

# Parâmetros individuais: D1 = 5, D2 = 1  ->  N = 3 + (1 mod 5) = 4
N = 4
TOTAL_AMOSTRAS = 20_000
TIMEOUT_S = 1.0          # 1 s sem receber nada = travamento
EXECUCOES = 3


def analisar(recebidas, produzidas):
    """
    Compara o que o consumidor recebeu com o que o produtor gerou.

    Parâmetros:
        recebidas (list): valores lidos pelo consumidor, na ordem em que foram lidos.
            Pode conter None (posição do buffer que nunca foi escrita).
        produzidas (int): quantas amostras o produtor chegou a colocar no buffer
            (amostras 0 .. produzidas-1).

    Retorno:
        dict com:
            consumidas: total de leituras feitas pelo consumidor;
            perdidas: amostras produzidas que nunca chegaram ao consumidor;
            duplicadas: leituras repetidas de uma amostra já recebida;
            invalidas: leituras de posição vazia (None), lixo do buffer.
    """
    vistas = set()
    duplicadas = 0
    invalidas = 0
    for valor in recebidas:
        if valor is None:
            invalidas += 1
        elif valor in vistas:
            duplicadas += 1
        else:
            vistas.add(valor)
    perdidas = sum(1 for v in range(produzidas) if v not in vistas)
    return {
        "consumidas": len(recebidas),
        "perdidas": perdidas,
        "duplicadas": duplicadas,
        "invalidas": invalidas,
    }


def rodar_experimento(nome_versao, executar_uma_vez):
    """
    Roda uma versão EXECUCOES vezes e imprime os resultados em tabela Markdown.

    Parâmetros:
        nome_versao (str): título mostrado no cabeçalho da saída.
        executar_uma_vez (callable): função sem argumentos que roda uma execução
            completa e devolve (recebidas, produzidas, travou).

    Retorno:
        list[dict]: resultado de cada execução (útil para testes).
    """
    print(f"=== {nome_versao} ===")
    print(f"N = {N} | amostras = {TOTAL_AMOSTRAS} | timeout = {TIMEOUT_S:.0f} s\n")
    resultados = []
    for i in range(1, EXECUCOES + 1):
        inicio = time.monotonic()
        recebidas, produzidas, travou = executar_uma_vez()
        duracao = time.monotonic() - inicio
        r = analisar(recebidas, produzidas)
        r.update(execucao=i, produzidas=produzidas, travou=travou, duracao=duracao)
        resultados.append(r)
        print(f"execução {i} terminou em {duracao:.2f} s"
              + ("  <-- TRAVOU" if travou else ""))

    print("\n| Execução | Produzidas | Consumidas | Perdidas | Duplicadas "
          "| Inválidas | Travou? |")
    print("|---|---|---|---|---|---|---|")
    for r in resultados:
        print(f"| {r['execucao']} | {r['produzidas']} | {r['consumidas']} "
              f"| {r['perdidas']} | {r['duplicadas']} | {r['invalidas']} "
              f"| {'sim' if r['travou'] else 'não'} |")
    return resultados
