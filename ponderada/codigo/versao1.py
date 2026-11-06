"""
versao1.py - Produtor/consumidor SEM sincronização (questão A4, versão 1).

Ponderada CC08 - Pulseira Tato
Autor: Pedro Jorge Alves Soares

A thread do sensor (produtora) e a do motor (consumidora) dividem um buffer
circular de N posições e um contador de posições ocupadas. Não há trava:
cada thread espera em laço (espera ocupada) e atualiza o contador com
"ler -> time.sleep(0) -> escrever". O sleep(0) devolve a CPU no pior momento
possível, entre a leitura e a escrita, e expõe a condição de corrida.

Nota sobre a espera ocupada: em Python, uma thread presa num laço vazio só
solta o GIL a cada 5 ms. Por isso o laço de espera também chama
time.sleep(0), como um sched_yield() em C. A thread continua testando o
contador sem parar (espera ocupada), só não segura a CPU à toa.

Uso: python3 versao1.py
"""

import threading
import time

from comum import N, TOTAL_AMOSTRAS, TIMEOUT_S, rodar_experimento


class Estado:
    """Memória compartilhada pelas duas threads (buffer, índices e contador)."""

    def __init__(self):
        """Cria o buffer vazio (None em todas as posições) e zera contador e índices."""
        self.buffer = [None] * N
        self.contador = 0      # posições ocupadas (variável compartilhada)
        self.entrada = 0       # próxima posição que o produtor escreve
        self.saida = 0         # próxima posição que o consumidor lê
        self.produzidas = 0
        self.recebidas = []
        self.travou = False
        self.parar = False     # avisa o produtor que o consumidor terminou


def produtor(estado, total):
    """
    Thread do sensor: gera as amostras 0, 1, 2, ... e coloca no buffer.

    Parâmetros:
        estado (Estado): memória compartilhada.
        total (int): quantas amostras gerar.

    Retorno:
        None. Atualiza estado.produzidas.
    """
    for amostra in range(total):
        while estado.contador >= N:          # espera ocupada: buffer cheio
            if estado.parar:
                return
            time.sleep(0)                    # cede a vez (ver nota no cabeçalho)
        estado.buffer[estado.entrada] = amostra
        estado.entrada = (estado.entrada + 1) % N
        # --- região crítica: ler e escrever o contador ---
        tmp = estado.contador
        time.sleep(0)                        # interrupção no pior momento
        estado.contador = tmp + 1
        # --------------------------------------------------
        estado.produzidas += 1


def consumidor(estado, total):
    """
    Thread do motor: retira amostras do buffer até ler `total` vezes.

    Parâmetros:
        estado (Estado): memória compartilhada.
        total (int): quantas leituras fazer.

    Retorno:
        None. Preenche estado.recebidas; marca estado.travou se ficar
        TIMEOUT_S segundos sem receber nada.
    """
    ultimo = time.monotonic()
    while len(estado.recebidas) < total:
        while estado.contador <= 0:          # espera ocupada: buffer vazio
            if time.monotonic() - ultimo > TIMEOUT_S:
                estado.travou = True
                estado.parar = True
                return
            time.sleep(0)                    # cede a vez (ver nota no cabeçalho)
        amostra = estado.buffer[estado.saida]
        estado.saida = (estado.saida + 1) % N
        # --- região crítica: ler e escrever o contador ---
        tmp = estado.contador
        time.sleep(0)                        # interrupção no pior momento
        estado.contador = tmp - 1
        # --------------------------------------------------
        estado.recebidas.append(amostra)
        ultimo = time.monotonic()
    estado.parar = True


def executar_uma_vez():
    """
    Roda uma execução completa com as duas threads.

    Retorno:
        tuple (recebidas, produzidas, travou).
    """
    estado = Estado()
    tp = threading.Thread(target=produtor, args=(estado, TOTAL_AMOSTRAS))
    tc = threading.Thread(target=consumidor, args=(estado, TOTAL_AMOSTRAS))
    tp.start()
    tc.start()
    tc.join()
    tp.join()
    return estado.recebidas, estado.produzidas, estado.travou


if __name__ == "__main__":
    rodar_experimento("Versão 1 - sem sincronização", executar_uma_vez)
