"""
versao3.py - Produtor/consumidor com a ORDEM TROCADA (questão A4, versão 3).

Ponderada CC08 - Pulseira Tato
Autor: Pedro Jorge Alves Soares

Igual à versão 2, com uma única diferença: o produtor faz wait(mutex) ANTES
de wait(vazio). Quando o buffer enche, o produtor dorme em vazio segurando
o mutex; o consumidor, que é o único que poderia liberar vazio, fica parado
em wait(mutex). Nenhum dos dois anda: deadlock.

Uso: python3 versao3.py
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
    Thread do sensor com a ordem ERRADA:
    wait(mutex) -> wait(vazio) -> escreve -> signal(mutex) -> signal(cheio).

    Parâmetros:
        estado (Estado): memória compartilhada.
        total (int): quantas amostras gerar.

    Retorno:
        None. Atualiza estado.produzidas.
    """
    for amostra in range(total):
        if not esperar(estado.mutex, estado):     # wait(mutex)  <- trocado
            return
        if not esperar(estado.vazio, estado):     # wait(vazio)  <- trocado
            return                                # (sai segurando o mutex)
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
    rodar_experimento("Versão 3 - wait(mutex) antes de wait(vazio)", executar_uma_vez)
