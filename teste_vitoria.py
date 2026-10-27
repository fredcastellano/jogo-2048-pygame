"""
Teste da condição de vitória do 2048.

Abre o jogo com um tabuleiro pré-carregado com quatro peças 512, para
chegar ao 2048 em poucos movimentos:
    ← (ou A)  funde 512+512 = 1024 nas duas linhas
    ↑ (ou W)  funde 1024+1024 = 2048 e mostra a tela de vitória

Reaproveita todo o código de jogo_2048.py: só a função que cria o
tabuleiro inicial é trocada.
"""

import jogo_2048


def grade_de_teste():
    return [
        [512, 512, 0, 0],
        [512, 512, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]


if __name__ == "__main__":
    jogo_2048.iniciar_grade = grade_de_teste
    jogo_2048.main()
