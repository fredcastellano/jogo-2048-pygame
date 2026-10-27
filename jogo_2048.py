import pygame
import random
import sys
from enum import Enum


                    # --- 1. ESTADOS DO JOGO ---
# Enum que representa os três estados possíveis da partida.
# Usar Enum evita o uso de strings ou números soltos no código, tornando as comparações mais legíveis e seguras.
class EstadoJogo(Enum):
    JOGANDO = 1
    VITORIA = 2
    DERROTA = 3


                    # --- 2. LÓGICA DO MOVIMENTO ---

def iniciar_grade():
    # Cria uma matriz 4x4 zerada e adiciona dois números iniciais (2 ou 4)
    # em posições aleatórias para começar a partida
    grade = [[0, 0, 0, 0] for _ in range(4)]
    grade = adicionar_numero(grade)
    grade = adicionar_numero(grade)
    return grade

def adicionar_numero(grade):
    # Coleta todas as células vazias (valor 0) da grade
    vazios = [(l, c) for l in range(4) for c in range(4) if grade[l][c] == 0]
    if vazios:
        l, c = random.choice(vazios)  # escolhe uma posição vazia aleatória
        grade[l][c] = 2 if random.random() < 0.9 else 4  # 90% chance de ser 2, 10% de ser 4
    return grade

def comprimir(linha):
    # Move todos os valores não-zero para o início da linha,
    # preenchendo o restante com zeros.
    # Ex: [0, 2, 0, 4] -> [2, 4, 0, 0]
    nova_linha = [i for i in linha if i != 0]
    nova_linha += [0] * (4 - len(nova_linha))
    return nova_linha

def fundir(linha):
    # Percorre a linha e funde elementos adjacentes de mesmo valor.
    # Cada par só pode ser fundido uma vez por movimento.
    # Ex: [2, 2, 4, 4] -> [4, 0, 8, 0] e retorna 12 pontos
    pontos = 0
    for i in range(3):
        if linha[i] != 0 and linha[i] == linha[i + 1]:
            linha[i] *= 2  # dobra o valor da célula da esquerda
            pontos += linha[i]  # acumula os pontos da fusão
            linha[i + 1] = 0  # zera a célula que foi absorvida
    return linha, pontos

def transpor(grade):
    # Troca linhas por colunas na matriz (rotaciona 90°).
    # Usado para reutilizar a lógica horizontal nos movimentos verticais.
    return [list(linha) for linha in zip(*grade)]

def inverter(grade):
    # Espelha cada linha da grade horizontalmente.
    # Usado para reutilizar a lógica de mover-para-esquerda
    # no movimento para direita.
    return [linha[::-1] for linha in grade]

def tem_movimentos(grade):
    # Verifica se o jogador ainda pode fazer alguma jogada.
    # Retorna True se houver célula vazia OU par adjacente que pode ser fundido.
    for l in range(4):
        for c in range(4):
            if grade[l][c] == 0: return True  # célula vazia
            if c < 3 and grade[l][c] == grade[l][c + 1]: return True  # par horizontal
            if l < 3 and grade[l][c] == grade[l + 1][c]: return True  # par vertical
    return False

def tem_vitoria(grade):
    # Retorna True se qualquer célula atingiu o valor 2048 (condição de vitória)
    return any(grade[l][c] >= 2048 for l in range(4) for c in range(4))

def processar_movimento(grade, comando):
    # Aplica um movimento (W/A/S/D) à grade usando a estratégia:
    # 1. Transformar a grade para que o movimento seja sempre "para a esquerda"
    # 2. Comprimir + Fundir + Comprimir cada linha
    # 3. Desfazer a transformação para restaurar a orientação original

    grade_antiga = [linha[:] for linha in grade]  # cópia para comparar depois
    nova_grade = []
    pontos_totais = 0
    cmd = comando.upper()

    # Transforma a grade conforme a direção do movimento
    if cmd == 'A':
        matriz_trabalho = grade  # esquerda: sem transformação
    elif cmd == 'D':
        matriz_trabalho = inverter(grade)  # direita: espelha horizontalmente
    elif cmd == 'W':
        matriz_trabalho = transpor(grade)  # cima: transpõe
    elif cmd == 'S':
        matriz_trabalho = inverter(transpor(grade))  # baixo: transpõe e espelha
    else:
        return grade, 0, False

    # Aplica comprimir -> fundir -> comprimir em cada linha
    for linha in matriz_trabalho:
        l_comp = comprimir(linha)  # empurra os números para a esquerda
        l_fund, pts = fundir(l_comp)  # funde pares adjacentes iguais
        l_final = comprimir(l_fund)  # remove os zeros gerados pela fusão
        nova_grade.append(l_final)
        pontos_totais += pts

    # Desfaz a transformação para restaurar a orientação original
    if cmd == 'D':
        nova_grade = inverter(nova_grade)
    elif cmd == 'W':
        nova_grade = transpor(nova_grade)
    elif cmd == 'S':
        nova_grade = transpor(inverter(nova_grade))

    # Só adiciona número novo se a grade realmente mudou após o movimento
    mudou = (nova_grade != grade_antiga)
    if mudou:
        nova_grade = adicionar_numero(nova_grade)
    return nova_grade, pontos_totais, mudou


                    # --- 3. CONFIGURAÇÕES VISUAIS ---
pygame.init()

# Dicionário de cores: mapeia cada valor de peça à sua cor de fundo.
# Chaves numéricas para as peças, strings para elementos da interface.
# As cores com 4 valores incluem transparência (canal alpha) para os overlays.
CORES = {
    'fundo': (187, 173, 160),
    'vazio': (205, 193, 180),
    'over_bg': (187, 173, 160, 200),  # cinza semi-transparente para game over
    'vitoria_bg': (50, 180, 100, 200),  # verde semi-transparente para vitória
    'texto_escuro': (119, 110, 101),
    'texto_claro': (249, 246, 242),
    2: (238, 228, 218), 4: (237, 224, 200),
    8: (242, 177, 121), 16: (245, 149, 99),
    32: (246, 124, 95), 64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97),
    512: (237, 200, 80), 1024: (237, 197, 63),
    2048: (237, 194, 46),
}

# Dimensões da janela: a grade ocupa LARGURA x LARGURA pixels,
# e o HUD (placar) ocupa uma faixa extra no topo de ALTURA_HUD pixels
LARGURA = 400
ALTURA_HUD = 80
TAMANHO_BLOCO = 80
MARGEM = 16

tela = pygame.display.set_mode((LARGURA, LARGURA + ALTURA_HUD))
pygame.display.set_caption("2048 Ultimate")
fonte_num = pygame.font.SysFont("arial, freesansbold", 36, bold=True)
fonte_num_pequena = pygame.font.SysFont("arial, freesansbold", 28, bold=True)  # para peças de 4 dígitos (1024, 2048...)
fonte_score = pygame.font.SysFont("arial, freesansbold", 28, bold=True)

def desenhar_interface(grade, score, estado):
    # Redesenha toda a tela a cada frame: fundo, placar, grade e overlay de fim de jogo
    tela.fill(CORES['fundo'])

    # Exibe a pontuação atual no topo da tela (área do HUD)
    texto_score = fonte_score.render(f"PONTOS: {score}", True, CORES['texto_claro'])
    tela.blit(texto_score, (MARGEM, 20))

    # Desenha cada célula da grade com sua cor e valor correspondente
    for l in range(4):
        for c in range(4):
            valor = grade[l][c]
            # Calcula a posição em pixels da célula (deslocada pelo HUD)
            x = MARGEM + c * (TAMANHO_BLOCO + MARGEM)
            y = ALTURA_HUD + MARGEM + l * (TAMANHO_BLOCO + MARGEM)

            # Busca a cor da peça; se for maior que 2048 usa a cor do 2048
            cor_bloco = CORES.get(valor, CORES[2048] if valor > 2048 else CORES['vazio'])
            pygame.draw.rect(tela, cor_bloco, (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO), border_radius=5)

            # Renderiza o número centralizado na célula (células 2 e 4 usam texto escuro)
            if valor != 0:
                cor_txt = CORES['texto_escuro'] if valor <= 4 else CORES['texto_claro']
                fonte = fonte_num if valor < 1000 else fonte_num_pequena  # números longos usam fonte menor para caber na peça
                txt = fonte.render(str(valor), True, cor_txt)
                rect_txt = txt.get_rect(center=(x + TAMANHO_BLOCO / 2, y + TAMANHO_BLOCO / 2))
                tela.blit(txt, rect_txt)

    # Se o jogo terminou, exibe um overlay semi-transparente com a mensagem adequada
    if estado != EstadoJogo.JOGANDO:
        s = pygame.Surface((LARGURA, LARGURA + ALTURA_HUD), pygame.SRCALPHA)

        if estado == EstadoJogo.VITORIA:
            s.fill(CORES['vitoria_bg'])
            titulo = "VOCE VENCEU!"
        else:
            s.fill(CORES['over_bg'])
            titulo = "GAME OVER!"

        tela.blit(s, (0, 0))
        cy = (LARGURA + ALTURA_HUD) / 2  # centro vertical da tela
        txt_titulo = fonte_num.render(titulo, True, (255, 255, 255))
        txt_reinicio = fonte_score.render("Pressione R para reiniciar", True, (255, 255, 255))
        tela.blit(txt_titulo, txt_titulo.get_rect(center=(LARGURA / 2, cy - 20)))
        tela.blit(txt_reinicio, txt_reinicio.get_rect(center=(LARGURA / 2, cy + 30)))

    pygame.display.update()

                    # --- 4. LOOP PRINCIPAL ---
def main():
    grade = iniciar_grade()
    score = 0
    estado = EstadoJogo.JOGANDO
    rodando = True  # controla o loop principal; vira False ao fechar a janela

    while rodando:
        desenhar_interface(grade, score, estado)
        for evento in pygame.event.get():
            # Fecha o jogo ao clicar no X da janela
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                # Se o jogo acabou, só aceita R para reiniciar
                if estado != EstadoJogo.JOGANDO:
                    if evento.key == pygame.K_r:
                        grade = iniciar_grade()
                        score = 0
                        estado = EstadoJogo.JOGANDO
                    continue

                # Mapeia as teclas de seta e WASD para os comandos de direção
                cmd = None
                if evento.key in (pygame.K_UP, pygame.K_w):
                    cmd = 'W'
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    cmd = 'S'
                elif evento.key in (pygame.K_LEFT, pygame.K_a):
                    cmd = 'A'
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    cmd = 'D'

                if cmd:
                    grade, pts, mudou = processar_movimento(grade, cmd)
                    if mudou:
                        score += pts
                        # Verifica vitória antes da derrota para cobrir o caso
                        # em que o 2048 é atingido na última célula disponível
                        if tem_vitoria(grade):
                            estado = EstadoJogo.VITORIA
                        elif not tem_movimentos(grade):
                            estado = EstadoJogo.DERROTA

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()