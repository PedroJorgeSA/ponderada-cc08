"""
versao2.py - Produtor/consumidor COM semáforos (questão A4, versão 2).

Ponderada CC08 - Pulseira Tato
Autor: Pedro Jorge Alves Soares

Mesmo buffer circular de N posições da versão 1, agora com três semáforos:
    vazio (começa em N): conta posições livres; o produtor espera nele;
    cheio (começa em 0): conta posições ocupadas; o consumidor espera nele;
    mutex (começa em 1): só uma thread mexe no buffer e nos índices por vez.
O time.sleep(0) continua dentro da região crítica, no mesmo lugar da versão 1,
para mostrar que a interrupção no pior momento deixa de causar estrago.

Uso: python3 versao2.py
"""

import threading
import time

from comum import N, TOTAL_AMOSTRAS, TIMEOUT_S, rodar_experimento


class Estado:
    """Memória compartilhada: buffer, índices e os três semáforos."""

    def __init__(self):
        """Cria o buffer vazio e os semáforos vazio = N, cheio = 0, mutex = 1."""
        self.buffer = [None] * N
        self.entrada = 0
        self.saida = 0
        self.vazio = threading.Semaphore(N)
        self.cheio = threading.Semaphore(0)
        self.mutex = threading.Semaphore(1)
        self.produzidas = 0
        self.recebidas = []
        self.travou = False
        self.parar = False


def esperar(semaforo, estado):
    """
    wait() que não prende o programa para sempre: tenta de 0,1 em 0,1 s
    e desiste se outra thread pediu para parar.

    Parâmetros:
        semaforo (threading.Semaphore): semáforo a decrementar.
        estado (Estado): usado para consultar estado.parar.

    Retorno:
        bool: True se conseguiu o semáforo, False se desistiu.
    """
    while not semaforo.acquire(timeout=0.1):
        if estado.parar:
            return False
    return True


def produtor(estado, total):
    """
    Thread do sensor: wait(vazio) -> wait(mutex) -> escreve -> signal(mutex) -> signal(cheio).

    Parâmetros:
        estado (Estado): memória compartilhada.
        total (int): quantas amostras gerar.

    Retorno:
        None. Atualiza estado.produzidas.
    """
    for amostra in range(total):
        if not esperar(estado.vazio, estado):     # wait(vazio)
            return
        if not esperar(estado.mutex, estado):     # wait(mutex)
            return
        estado.buffer[estado.entrada] = amostra
        time.sleep(0)                             # interrupção no pior momento
        estado.entrada = (estado.entrada + 1) % N
        estado.produzidas += 1
        estado.mutex.release()                    # signal(mutex)
        estado.cheio.release()                    # signal(cheio)


def consumidor(estado, total):
    """
    Thread do motor: wait(cheio) -> wait(mutex) -> lê -> signal(mutex) -> signal(vazio).

    Parâmetros:
        estado (Estado): memória compartilhada.
        total (int): quantas amostras consumir.

    Retorno:
        None. Preenche estado.recebidas; marca estado.travou se um wait
        passar de TIMEOUT_S segundos.
    """
    for _ in range(total):
        if not estado.cheio.acquire(timeout=TIMEOUT_S):   # wait(cheio)
            estado.travou = True
            break
        if not estado.mutex.acquire(timeout=TIMEOUT_S):   # wait(mutex)
            estado.travou = True
            break
        amostra = estado.buffer[estado.saida]
        time.sleep(0)                             # interrupção no pior momento
        estado.saida = (estado.saida + 1) % N
        estado.mutex.release()                    # signal(mutex)
        estado.vazio.release()                    # signal(vazio)
        estado.recebidas.append(amostra)
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
    rodar_experimento("Versão 2 - com semáforos", executar_uma_vez)
