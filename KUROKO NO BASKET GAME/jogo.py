#========== IMPORTS ===========
#
#==============================
import pgzrun, random, os
import pygame
from pgzero.actor import Actor
import schedule
from pgzero.rect import Rect
#======== Comentário =========
# comentário para salvar o jogo
#==============================
"""if os.path.exists('jogo/save.txt'):
                    carregar_jogo() 
                else:
                    mode = 'intro' # COLOCAR INTRO DEPOIS"""

#============= VARIÁVEIS ============
#
#====================================

# IDEIA : FAZER LISTA TIME 1 e 2, Se boneco tal tocar no time 2 (vale pra qualquer elemento) rouba a bola (dai n precisa fzr interação com todos)
quadra = Actor('quadra.jpg')

tempo_de_jogo = 300  # Tempo de jogo em segundos (5 minutos)
tempo_de_jogo_regride = False

mode = 'lobby' #Define o local do jogo

WIDTH = quadra.width
HEIGHT = quadra.height
TITLE = "Kuroko no Basket" # Título do jogo
FPS = 60 # Quadros por segundo

despertar = False
posse = 'empty'

pontotime1 = 0
pontotime2 = 0
level = 1 #O Nível do personagem atual, que vai mudar as habilidades ou as suas propriedades, como velocidade, stamina, menor tempo de recarga, 
dinheiro = 0 # DINHEIRO PARA COMPRAR SPINS (GIROS) DE HABILIDADE
stamina = 100  # Stamina máxima
classe = 'aomine'  # Classe inicial do jogador

vitrine_class = Actor('girar/absoluto.png', (WIDTH/2, HEIGHT/2 - 100)) # Vitrine de classe

kuroko = Actor('kuroko.png', (400, 300)) # KUROKO É O PLAYER
oponente = Actor('kise.png', (1000, HEIGHT/2)) # BOT

ability1_button = Actor('habilidadekurokovarianteparado1.png', (WIDTH - 200, HEIGHT - 100))
ability2_button = Actor('habilidadekurokovarianteparado2.png', (WIDTH - 100, HEIGHT - 100))

play = Actor('play.png', center=(WIDTH/2, HEIGHT-100))

ball = Actor('ball_00.png', center=(WIDTH/2, HEIGHT/2), size=(30,55555))

sexta = Actor('sextateste.png', (WIDTH - 160, HEIGHT/2))

sexta2 = Actor('sextateste.png', (160, HEIGHT/2))
sexta2._surf = pygame.transform.flip(sexta2._orig_surf, True, False)
spin_button = Actor('spin.png', (100, HEIGHT - 100)) # GIRA a classe
voltar_button = Actor('voltar.png', (WIDTH/2, HEIGHT - 100))
arremesso_especial = 0
kuroko_invisible = False
moggado_por_akashi = False #quando fica moggado, ele fica no chão, sem habilidade e sem andar.
bot_moggado_por_akashi = False # o mesmo, mas para o bot

# Estado da bola
ball_pegou = False
ball_arremessada = False
ball_dx = 0
ball_dy = 0
# Animação da bola
ball_animation_frame = 0
ball_animation_timer = 0
ball_frame_time = 0.1  # Tempo em segundos entre cada frame da animação
# Cooldown da habilidade 1
ability1_cooldown = 0
ability1_cooldown_max = 10  # Tempo máximo de cooldown em segundos
ability2_cooldown = 0
ability2_cooldown_max = 15  # Tempo máximo de cooldown em segundos
drible_cooldown = 0
drible_cooldown_max = 5  # Tempo máximo de cooldown em segundos
kagami_ate_cesta = False
tempo_skill = 0
kagami_defesa = False
drible = False
frase_ativada = False
frase_aura = {"akashi": ["E","Eu","Eu s","Eu so","Eu sou","Eu sou a","Eu sou ab","Eu sou abs","Eu sou abso","Eu sou absol","Eu sou absolu","Eu sou absolut","Eu sou absoluto","Eu sou absoluto!"], 
              "aomine": ["O único que pode me derrotar sou eu mesmo!"]}
dono_da_frase = "akashi" 
letra_atual = 0 # FRASE DO AKASHI TEM 14 LETRA ATUAL
giros_restantes = 3 #giros grátis ou códigos
rastros_jogador = []
rastros_bola = []
tempo_rastro = 10
tempo_arremesso = 0
ax = 0
aomine_drible = False

def adicionar_rastro():
    global rastros_jogador, classe

    imagem = kuroko._surf.copy()

    # Deixa a imagem azul
    azul = pygame.Surface(imagem.get_size(), pygame.SRCALPHA)
    if classe == "akashi":
        azul.fill((255, 0, 0, 120))  # Vermelho para Akashi
    elif classe == "kagami":
        azul.fill((255, 165, 0, 120))  # Laranja para Kagami
    else:
        azul.fill((0, 100, 255, 120))
    imagem.blit(azul, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    rastros_jogador.append({
        "imagem": imagem,
        "pos": (kuroko.x - 30, kuroko.y - 60),
        "tempo": 0.15
    })

def rastro_bola():
    global rastros_bola, classe

    imagem = ball._surf.copy()

    # Deixa a imagem azul
    azul = pygame.Surface(imagem.get_size(), pygame.SRCALPHA)
    if classe == "midorima":
        azul.fill((50, 255, 50, 120)) # verde para midorima
    elif classe == "kuroko":
        azul.fill((255, 165, 0, 120))  # azul para kuroko
    else:
        azul.fill((0, 100, 255, 120))
    imagem.blit(azul, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    rastros_bola.append({
        "imagem": imagem,
        "pos": (ball.x - 30, ball.y - 60),
        "tempo": 0.15
    })



def salvar_jogo():
    global level, dinheiro
    save = open('jogo/save.txt', 'w')
    save.write(str(level) + '\n')
    save.write(str(dinheiro)+ '\n')
    save.close()
    print('jogo salvo')

def carregar_jogo():
    global level, dinheiro
    if os.path.exists('jogo/save.txt'):
        save = open('jogo/save.txt', 'r')
        linhas = save.readlines()
        level = int(linhas[0].strip())
        dinheiro = str(linhas[1].strip())
        save.close()
        print('jogo carregado')
    else:
        create_save()

def create_save():
    global level, dinheiro
    level = 1 
    dinheiro = 0


def arremesso_especial_midorima():
    """Arremesso especial rápido do Midorima"""
    global ball_arremessada, ball_dx, ball_dy, ball_pegou, arremesso_especial, ability1_cooldown

    # Calcular vetor até a cesta
    delta_x = sexta.x - ball.x
    delta_y = sexta.y - ball.y
    
    # Normalizar a direção
    distancia = (delta_x**2 + delta_y**2) ** 0.5
    if distancia > 0:
        ball_dx = delta_x / distancia
        ball_dy = delta_y / distancia
    else:
        ball_dx = 1
        ball_dy = 0
    
    # Ativar arremesso especial (velocidade 1000 px/s)
    arremesso_especial = 1
    ball_arremessada = True
    ball_pegou = False
    ability1_cooldown = ability1_cooldown_max

def spin():
    global dinheiro, classe, giros_restantes
    #giro da sorte dps
    if giros_restantes > 0 or dinheiro >= 100:
        if giros_restantes > 0:
            giros_restantes -= 1
        elif dinheiro >= 100:
            dinheiro -= 100
        a =random.randint(1,100)
        if a == 100:
            classe = 'aomine'
            #AOMINE (PANTERA)
        elif a > 2 and a <=25:
            classe = 'kuroko'
            #kuroko (SOMBRA) 
        elif a >25 and a <=50:
            classe = 'kise'
            #kise (Réplica)
        elif a >50 and a <=75:
            classe = 'kagami'
            #Kagami (Saltador)
        elif a >75 and a <100:
            classe = 'midorima'
            #Midorima (Arremesso perfeito)
        elif a == 1:
            classe = 'akashi'
            #Akashi (Absoluto)
        elif a == 2:
            classe = 'murasakibara'
            #Murasakibara (Impenetrável)

def draw():
    global mode, tempo_de_jogo, pontotime1, pontotime2
    
    if mode == 'lobby':
        screen.clear()
        screen.fill((200, 120, 0))
        ball.draw()
        kuroko.draw()
        
        ability1_button.draw()
        ability2_button.draw()
        screen.draw.text(f'Level: {level}', (10, 10), color='white', fontsize=30)
        screen.draw.text(f'Dinheiro: {dinheiro}', (10, 40), color='white', fontsize=30)
        screen.draw.text(f'Classe:{classe}', (10, 70), color='white', fontsize=30)
        play.draw()
        spin_button.draw()

    elif mode == 'spin':
        screen.clear()
        screen.fill((0, 0, 0))
        screen.draw.text(f'Classe sorteada: {classe}', (WIDTH/2 - 100, HEIGHT/2), color='white', fontsize=30)
        vitrine_class.draw()
        screen.draw.text(f'Dinheiro: {dinheiro}', (WIDTH/2 - 100, HEIGHT/2 + 50), color='white', fontsize=30)
        screen.draw.text(f'Level: {level}', (WIDTH/2 - 100, HEIGHT/2 + 100), color='white', fontsize=30)
        voltar_button.draw()
        spin_button.draw()
        screen.draw.text('Clique para voltar ao lobby', (WIDTH/2 - 150, HEIGHT/2 + 150), color='white', fontsize=30)
    elif mode == 'game':
        screen.clear()
        quadra.draw()
        #desenha os rastros do jogador
        for rastro in rastros_jogador:
            screen.blit(rastro["imagem"], rastro["pos"])
        if ball_arremessada == True:
            for x, y in rastros_bola:
                if classe == "midorima":
                    screen.draw.filled_circle((x, y), 10, (0, 255, 0))
                elif classe == "kuroko":
                    screen.draw.filled_circle((x, y), 15, (0, 200, 255))
                elif classe == "aomine":
                    screen.draw.filled_circle((x, y), 3, (0, 100, 100))
        kuroko.draw()
        oponente.draw()

        ball.draw()
        sexta.draw()
        sexta2.draw()

        # ============= PLACAR ==============
        screen.draw.text(f'Pontos Time 1:  {pontotime1}', (10, 50), color='red', fontsize=30)
        screen.draw.text(f'Pontos Time 2:  {pontotime2}', (WIDTH - 220, 50), color='blue', fontsize=30)
        screen.draw.text(f'Tempo de Jogo:  {int(tempo_de_jogo)}s', (WIDTH/2 - 100, 50), color='white', fontsize=30)
        # Barra de stamina vertical ao lado do Kuroko
        barra_x = kuroko.x + 30  # À direita do Kuroko
        barra_y = kuroko.y - 50  # Centralizada verticalmente
        barra_largura = 10
        barra_altura_total = 100
        barra_altura_atual = (stamina / 100) * barra_altura_total
        ability1_button.draw()
        ability2_button.draw()
        
        # Cooldown visual da habilidade 1
        if ability1_cooldown > 0:
            cooldown_percent = ability1_cooldown / ability1_cooldown_max
            cooldown_altura = ability1_button.height * cooldown_percent
            # Retângulo semi-transparente cobrindo a habilidade
            overlay = pygame.Surface((ability1_button.width, cooldown_altura))
            overlay.set_alpha(150)  # Transparência
            overlay.fill((0, 0, 0))  # Preto
            screen.blit(overlay, (ability1_button.x - ability1_button.width // 2, 
                                   ability1_button.y - ability1_button.height // 2 + (ability1_button.height - cooldown_altura)))
            # Contador de tempo
            screen.draw.text(f'{ability1_cooldown:.1f}s', 
                            (ability1_button.x - 15, ability1_button.y - ability1_button.height // 2 - 20),
                            color='white', fontsize=16)
        #COOLDOWN VISUAL DA HABILIDADE 2
        if ability2_cooldown > 0:
            cooldown_percent = ability2_cooldown / ability2_cooldown_max
            cooldown_altura = ability2_button.height * cooldown_percent
            # Retângulo semi-transparente cobrindo a habilidade
            overlay = pygame.Surface((ability2_button.width, cooldown_altura))
            overlay.set_alpha(150)  # Transparência
            overlay.fill((0, 0, 0))  # Preto
            screen.blit(overlay, (ability2_button.x - ability2_button.width // 2, 
                                   ability2_button.y - ability2_button.height // 2 + (ability2_button.height - cooldown_altura)))
            # Contador de tempo
            screen.draw.text(f'{ability2_cooldown:.1f}s', 
                            (ability2_button.x - 15, ability2_button.y - ability2_button.height // 2 - 20),
                            color='white', fontsize=16)

        
        # Fundo da barra (cinza)
        screen.draw.filled_rect(Rect(barra_x, barra_y, barra_largura, barra_altura_total), (100, 100, 100))
        # Barra atual (verde se cheia, vermelho se baixa)
        cor = (0, 255, 0) if stamina > 50 else (255, 0, 0) if stamina > 0 else (255, 255, 255)
        screen.draw.filled_rect(Rect(barra_x, barra_y + (barra_altura_total - barra_altura_atual), barra_largura, barra_altura_atual), cor)
        if frase_ativada == True:
            screen.draw.text(frase_aura[dono_da_frase][letra_atual], (kuroko.x - 80, kuroko.y - 100), color='red', fontsize=30)
        if mode == "game" and tempo_de_jogo <= 0 and pontotime1 != pontotime2:
            mode = "endgame"
        elif mode == "game" and tempo_de_jogo <= 0:
            screen.draw.text("Morte súbita! A próxima sexta define o jogo", (WIDTH/2 - 220, 90), color='blue', fontsize=30)
    elif mode == "endgame":
        screen.clear()
        screen.fill((0, 0, 0))
        if pontotime1 > pontotime2:
            screen.draw.text("Time 1 vence!", (WIDTH/2 - 100, HEIGHT/2), color='white', fontsize=50)
            
            #screen.draw.text("Mais sextas:", (WIDTH/2 - 100, HEIGHT/2 - 100), color='white', fontsize=50)
            #DAR DINHEIRO E FAZER BOTÃO DE VOLTAR
        elif pontotime2 > pontotime1:
            screen.draw.text("Time 2 vence!", (WIDTH/2 - 100, HEIGHT/2), color='white', fontsize=50)
            
        voltar_button.draw()
    
def on_key_down(key):
    global tempo_arremesso, aomine_drible, ax, dono_da_frase, frase_ativada, drible_cooldown_max, drible_cooldown, drible, kagami_defesa, tempo_skill, kagami_ate_cesta, moggado_por_akashi, bot_moggado_por_akashi, stamina, kuroko_invisible, posse, ball_arremessada, ball_dx, ball_dy, ball_pegou, ability1_cooldown, ability2_cooldown, despertar, arremesso_especial
    if not moggado_por_akashi: # Se não tiver sido moggado pelo Akashi, pode usar as habilidades e se mover normalmente
        if despertar == False:# se não tiver despertado ainda, HABILIDADES NORMAIS
            
            if key == keys.C: # Habilidade 1
                if ball_pegou == False: # variante SEM A BOLA
                    if ability1_cooldown <= 0: # se o cooldown da habilidade 1 for 0
                        if classe == 'kuroko': # habilidade 1 do Kuroko
                            kuroko._surf.set_alpha(100)# opacidade reduzida para 100 (invisível)
                            kuroko_invisible = True
                            ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                            
                            # Limpar tarefas anteriores de invisibilidade
                            schedule.clear('invisibilidade')  # Remove tarefas com a tag
                            
                            def voltar_normal():
                                global kuroko_invisible
                                kuroko._surf.set_alpha(255) # Restaura opacidade para 255 (normal)
                                kuroko_invisible = False
                                
                            schedule.every(5).seconds.do(voltar_normal).tag('invisibilidade') # Restaura opacidade após 5 segundos
                        
                        elif classe == 'kise':
                            pass  # Habilidade 1 do Kise
                        elif classe == 'kagami':
                            if ability1_cooldown <= 0: # se o cooldown da habilidade 1 for 0
                                ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                                ax = 0
                                
                                schedule.clear('pulo')  # Limpa qualquer rastro anterior
                                def criar_rastro():
                                    global ax
                                    kuroko.y -= 40
                                    ax += 1
                                    adicionar_rastro()

                                    if ax >= 10:  # Se sair da tela, para de criar rastros
                                        return schedule.CancelJob
                            
                                schedule.every(0.05).seconds.do(criar_rastro).tag('pulo')  # Cria rastro a cada 0.1 segundos
                                
                        elif classe == 'midorima':
                            pass  # Habilidade 1 do Midorima
                        elif classe == 'akashi':
                            pass  # Habilidade 1 do Akashi
                        elif classe == 'aomine':
                            if ability1_cooldown <= 0: # se o cooldown da habilidade 1 for 0
                                ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                                ax = 0
                                aomine_drible = True
                                schedule.clear('rastro')  # Limpa qualquer rastro anterior
                                def criar_rastro():
                                    global ax, aomine_drible
                                    
                                    ax += 1
                                    adicionar_rastro()

                                    if ax >= 15:  # Se sair da tela, para de criar rastros
                                        aomine_drible = False
                                        return schedule.CancelJob
                            
                                schedule.every(0.05).seconds.do(criar_rastro).tag('rastro')  # Cria rastro a cada 0.1 segundos
                        elif classe == 'murasakibara':
                            
                            if posse == 'oponente' and abs(kuroko.x - oponente.x) < 250 and abs(kuroko.y - oponente.y) < 250:
                                ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1

                                posse = "kuroko"
                                ball_pegou = True                                
                                arremesso_especial = 0
                                ball_arremessada = True
                                ball.x += 100
                                # Definir direção baseada nas teclas WSAD
                                ball_dx = 0
                                ball_dy = 0
                                if keyboard.w:
                                    ball_dy = -1
                                if keyboard.s:
                                    ball_dy = 1
                                if keyboard.a:
                                    ball_dx = -1
                                if keyboard.d:
                                    ball_dx = 1
                                # Se nenhuma direção, arremessar para frente (direita)
                                if ball_dx == 0 and ball_dy == 0:
                                    ball_dx = 1
                                #não pega a mais a bola, poís já está arremessada
                                ball_pegou = False

                elif ball_pegou == True: # variante COM A BOLA
                    if classe == 'kuroko':
                        if abs(kuroko.y - sexta.y) < 200 and abs(kuroko.x - sexta.x) < 200 and ability1_cooldown <= 0:
                            ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                            ball_dx = 0
                            ball_dy = 0
                            if keyboard.w:
                                ball_dy = -1
                            if keyboard.s:
                                ball_dy = 1
                            if keyboard.a:
                                ball_dx = -1
                            if keyboard.d:
                                ball_dx = 1
                            # Se nenhuma direção, arremessar para frente (direita)
                            if ball_dx == 0 and ball_dy == 0:
                                ball_dx = 1
                            arremesso_especial = 4
                            tempo_arremesso = 0
                            ball_arremessada = True
                            ball_pegou = False

                             #TIPO A DO MIDORIMA, MAS RETO PRA CIMA, NÃO ROUBÁVEL E COM AURA AZUL

                        #se n, faz o passe
                        # Habilidade 1 do Kuroko com a bola
                        #TERIA Q TER O ONLINE PARA FZR ESSA HABILIDADE COM A BOLA
                        #HABILIDADE: PASSE FANTASMA
                        #Referência: https://www.youtube.com/watch?v=jWVe02jgGLM
                        #minutagem: 1:15 até 1:20

                    elif classe == 'kise':     
                        pass  # Habilidade 1 do Kise
                    elif classe == 'kagami':
                        if ability1_cooldown <= 0: # se o cooldown da habilidade 1 for 0
                                ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                                ax = 0
                                
                                schedule.clear('pulo')  # Limpa qualquer rastro anterior
                                def criar_rastro():
                                    global ax, ball_pegou, arremesso_especial, ball_arremessada
                                    kuroko.y -= 30

                                    ax += 1
                                    adicionar_rastro()

                                    if ax >= 10:  # Se sair da tela, para de criar rastros
                                        arremesso_especial = 2
                                        ball_arremessada = True
                                        return schedule.CancelJob
                                    
                                schedule.every(0.01).seconds.do(criar_rastro).tag('pulo')  # Cria rastro a cada 0.1 segundos

                    elif classe == 'midorima':
                        if ability1_cooldown <= 0 and ball_pegou == True: # se o cooldown da habilidade 1 for 0 E tiver a bola
                            ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                            ball_dx = 0
                            ball_dy = 0
                            if keyboard.w:
                                ball_dy = -1
                            if keyboard.s:
                                ball_dy = 1
                            if keyboard.a:
                                ball_dx = -1
                            if keyboard.d:
                                ball_dx = 1
                            # Se nenhuma direção, arremessar para frente (direita)
                            if ball_dx == 0 and ball_dy == 0:
                                ball_dx = 1
                            arremesso_especial = 3
                            tempo_arremesso = 0
                            ball_arremessada = True
                            ball_pegou = False
                            





                    elif classe == 'akashi':#me olhe de baixo (se bot estiver perto, ele é moggado)
                        if abs(kuroko.x - oponente.x) < 400 and abs(kuroko.y - oponente.y) < 400:
                            if ability1_cooldown <= 0 and ball_pegou == True: # se o cooldown da habilidade 1 for 0 E tiver a bola
                                ability1_cooldown = ability1_cooldown_max # inicia o cooldown da habilidade 1
                                dono_da_frase = "akashi"
                                frase_ativada = True
                                
                                bot_moggado_por_akashi = True
                                schedule.clear('mogado')
                                # O Kuroko fica caído no chão, sem habilidade e sem andar, por 5 segundos
                                def levantar():
                                    global frase_ativada, letra_atual
                                    global bot_moggado_por_akashi
                                    bot_moggado_por_akashi = False
                                    print("Bot levantou!")
                                    frase_ativada = False
                                    letra_atual = 0
                                    return schedule.CancelJob
                                schedule.every(5).seconds.do(levantar).tag('mogado') # Levanta após 5 segundos
                    elif classe == 'aomine':
                        pass  # Habilidade 1 do Aomine
                    elif classe == 'murasakibara':
                        pass  # MARTELO DE THOR
            if key == keys.V: # Habilidade 2   
                if ball_pegou == False: # variante SEM A BOLA
                    if ability2_cooldown <= 0: # se o cooldown da habilidade 2 for 0
                        if classe == 'kuroko': # habilidade 2 do Kuroko sem a bola
                            if keyboard.a:
                                kuroko.x -= 150
                                ability2_cooldown = ability2_cooldown_max
                            elif keyboard.d:
                                kuroko.x += 150
                                ability2_cooldown = ability2_cooldown_max
                            elif keyboard.w:
                                kuroko.y -= 150
                                ability2_cooldown = ability2_cooldown_max
                            elif keyboard.s:
                                kuroko.y += 150
                                ability2_cooldown = ability2_cooldown_max
                            if kuroko.colliderect(ball) and ball_pegou == False and ball_arremessada == True:
                                ball_arremessada = False
                                ball_pegou = True
                                ball.x = kuroko.x + 30
                                ball.y = kuroko.y
                        elif classe == 'kise':
                            pass  # Habilidade 2 do Kise
                        elif classe == 'kagami' and ability2_cooldown <= 0:
                            ability2_cooldown = ability2_cooldown_max
                            kagami_defesa = True
                            tempo_skill = 0
                        elif classe == 'midorima': 
                            ability2_cooldown = ability2_cooldown_max
                            stamina = 100  # Stamina máxima

                            # Habilidade 2 do Midorima
                        elif classe == 'akashi':
                            pass  # Habilidade 2 do Akashi
                        elif classe == 'aomine':
                            pass  # Habilidade 2 do Aomine

                        
                elif ball_pegou == True: # variante COM A BOLA
                    if classe == 'kuroko':
                        if ability2_cooldown <= 0:
                            if keyboard.a:
                                kuroko.x -= 150
                                ability2_cooldown = ability2_cooldown_max
                            elif keyboard.d:
                                kuroko.x += 350
                                ability2_cooldown = ability2_cooldown_max
                            elif keyboard.w:
                                kuroko.y -= 150
                                ability2_cooldown = ability2_cooldown_max
                            elif keyboard.s:
                                kuroko.y += 150
                                ability2_cooldown = ability2_cooldown_max
                            ball.x = kuroko.x
                            ball.y = kuroko.y 
                        # PARA A HABILIDADE DE DRIBLE COM A BOLA PRECISO DE OUTRO PLAYER PARA A CUTSCIENE ENT N DA PRA FZR AGR
                        #HABILIDADE : DRIBLE DAS SOMBRAS
                        #Referência: https://www.youtube.com/shorts/wLZ6f_yZyf0
                        
                    elif classe == 'kise':
                        pass  # Habilidade 2 do Kise
                    elif classe == 'kagami' and ability2_cooldown <= 0:
                        ability2_cooldown = ability2_cooldown_max
                        kagami_ate_cesta = True
                        tempo_skill = 0
                         
                        '''if kuroko.x < sexta.x:
                                                kuroko.x += 200
                                            if kuroko.y < sexta.y:
                                                kuroko.y += 200
                                            if kuroko.y > sexta.y:
                                                kuroko.y -= 200
                                            if ability2_cooldown <= 0:
                                                ability2_cooldown = ability2_cooldown_max
                                                def enterrada():
                                                    if kuroko.x < sexta.x:
                                                        kuroko.x += 40
                                                    if kuroko.y < sexta.y:
                                                        kuroko.y += 40
                                                    if kuroko.y > sexta.y:
                                                        kuroko.y -= 40
                                                enterrada()
                                                for i in range(10):
                                                    enterrada()'''
                    elif classe == 'midorima':
                        pass  # Habilidade 2 do Midorima
                    elif classe == 'akashi':
                        if ability2_cooldown <= 0: # se o cooldown da habilidade 2 for 0 E tiver a bola
                            ability2_cooldown = ability2_cooldown_max # inicia o cooldown da habilidade 1
                            ax = 0
                            drible = True
                            schedule.clear('rastro')  # Limpa qualquer rastro anterior
                            def criar_rastro():
                                global ax, drible
                                
                                ax += 1
                                adicionar_rastro()

                                if ax >= 15:  # Se sair da tela, para de criar rastros
                                    drible = False
                                    return schedule.CancelJob
                        
                            schedule.every(0.05).seconds.do(criar_rastro).tag('rastro')  # Cria rastro a cada 0.1 segundos
                    elif classe == 'aomine':
                        if kuroko.x > sexta.x and abs(kuroko.y - sexta.y) < 100:
                            '''bot_moggado_por_akashi = True
                            schedule.clear('a')
                            # O Kuroko fica caído no chão, sem habilidade e sem andar, por 5 segundos
                            def levantar():
                                global frase_ativada, letra_atual
                                global bot_moggado_por_akashi
                                bot_moggado_por_akashi = False
                                print("Bot levantou!")
                                frase_ativada = False
                                letra_atual = 0
                                return schedule.CancelJob
                            
                            schedule.every(5).seconds.do(levantar).tag('a') # Levanta após 5 segundos
                            kuroko._surf = pygame.transform.rotate(kuroko._surf, 90)'''
                            if ability2_cooldown <= 0: # se o cooldown da habilidade 2 for 0
                                ability2_cooldown = ability2_cooldown_max # inicia o cooldown da habilidade 2
                                kuroko._surf = pygame.transform.rotate(kuroko._surf, 90)
                                ball_dx = -1
                                arremesso_especial = 5
                                ball_arremessada = True
                                ball_pegou = False
                                tempo_arremesso = 0
                
                
        elif despertar == True: # se já tiver despertado, HABILIDADES DESPERTAR
            pass # implementar habilidades de despertar depois
    if not moggado_por_akashi: # se for moggado pelo Akashi, vai ficar caido no chão
        if key == keys.A:#mudar skin esquerda dependendo do personagem
            kuroko._surf = pygame.transform.flip(kuroko._orig_surf, True, False)
        
        if key == keys.D:#mudar skin direita dependendo do personagem
            alpha = kuroko._surf.get_alpha() or 255  # Preservar opacidade
            if classe == 'kuroko':
                kuroko.image = 'kuroko.png'
            elif classe == 'kise':
                kuroko.image = 'kise.png'
            elif classe == 'kagami':
                kuroko.image = 'kagami.png'
            elif classe == 'midorima':
                kuroko.image = 'midorima.png'
            elif classe == 'akashi':
                kuroko.image = 'akashi.png'
            elif classe == 'aomine':
                kuroko.image = 'aomine.png'
            elif classe == 'murasakibara':
                kuroko.image = 'murasakibara.png'
            kuroko._surf.set_alpha(alpha)  # Restaurar opacidade
    else: 
        #AQUI, DEPENDENDO DO PERSONAGEM, ELE FICA MOGGADO DE UMA FORMA DIFERENTE, POR EXEMPLO, O KUROKO FICA CAIDO NO CHÃO, O AOMINE FICA DE COSTAS, O AKASHI FICA COM A CABEÇA PARA BAIXO, ETC
        if classe == 'kuroko':
            kuroko.image = 'kuroko_chao.png'
        elif classe == 'kise':
            kuroko.image = 'kise_chao.png'
        elif classe == 'kagami':
            kuroko.image = 'kagami_chao.png'
        elif classe == 'midorima':
            kuroko.image = 'midorima_chao.png'
        elif classe == 'akashi':
            kuroko.image = 'akashi_chao.png'
        elif classe == 'aomine':
            kuroko.image = 'aomine_chao.png'
        elif classe == 'murasakibara':
            kuroko.image = 'murasakibara_chao.png'

    if key == keys.Q and ball_pegou and drible_cooldown <= 0: #DRIBLE BÁSICO
        drible_cooldown = drible_cooldown_max
        drible = True
        def driblando():
            global drible
            drible = False
            print("Drible realizado!")
            return schedule.CancelJob
        schedule.every(0.5).seconds.do(driblando)# uma vez
    if key == keys.SPACE and ball_pegou: #ARREMESSO Normal

        arremesso_especial = 0
        ball_arremessada = True

        # Definir direção baseada nas teclas WSAD
        ball_dx = 0
        ball_dy = 0
        if keyboard.w:
            ball_dy = -1
        if keyboard.s:
            ball_dy = 1
        if keyboard.a:
            ball_dx = -1
        if keyboard.d:
            ball_dx = 1
        # Se nenhuma direção, arremessar para frente (direita)
        if ball_dx == 0 and ball_dy == 0:
            ball_dx = 1
        #não pega a mais a bola, poís já está arremessada
        ball_pegou = False


def on_key_up(key):
    # Função mantida para compatibilidade, mas lógica de hold do Midorima está no update()
    pass
def on_mouse_down(button, pos):
    global mode, pontotime1, pontotime2, tempo_de_jogo, tempo_de_jogo_regride, dinheiro
    if button == mouse.LEFT:
        if spin_button.collidepoint(pos):
            if mode == 'lobby':
                mode = "spin"
            elif mode == 'spin':
                spin()
        if mode == 'lobby' and play.collidepoint(pos):
            mode = 'game'
            pontotime2 = 0
            pontotime1 = 0
            tempo_de_jogo = 300  # Reinicia o tempo de jogo ao começar
            tempo_de_jogo_regride = True
        if mode == 'spin' and voltar_button.collidepoint(pos):
            mode = 'lobby'
        if mode == 'endgame' and voltar_button.collidepoint(pos):
            if pontotime1 > pontotime2:
                screen.draw.text("Time 1 vence!", (WIDTH/2 - 100, HEIGHT/2), color='white', fontsize=50)
                dinheiro += 100
            #screen.draw.text("Mais sextas:", (WIDTH/2 - 100, HEIGHT/2 - 100), color='white', fontsize=50)
            #DAR DINHEIRO E FAZER BOTÃO DE VOLTAR
            elif pontotime2 > pontotime1:
                screen.draw.text("Time 2 vence!", (WIDTH/2 - 100, HEIGHT/2), color='white', fontsize=50)
                dinheiro += 50
            mode = 'lobby'



def update(dt):
    global rastros_bola, tempo_arremesso, ax, vitrine_class, aomine_drible, frase_ativada, drible, drible_cooldown, kagami_defesa,tempo_skill, kagami_ate_cesta, bot_moggado_por_akashi, moggado_por_akashi, kuroko_invisible, posse, tempo_de_jogo, tempo_de_jogo_regride,stamina, ball_pegou, ball_arremessada, pontotime1, ball_animation_timer, ball_animation_frame, ability1_cooldown, ability2_cooldown, pontotime2, arremesso_especial, ball_dx, ball_dy
    if frase_ativada == True:
        global letra_atual
        if letra_atual < len(frase_aura[dono_da_frase]) - 1:
            letra_atual += 1  # Ajuste a velocidade de avanço da frase conforme necessário

    if mode == 'spin':
        if classe == 'kuroko':
            vitrine_class.image = 'girar/shadow.png'
        elif classe == 'kise':
            vitrine_class.image = 'girar/replica.png'
        elif classe == 'kagami':
            vitrine_class.image = 'girar/saltador_incansavel.png'
        elif classe == 'midorima':
            vitrine_class.image = 'girar/arremesso_perfeito.png'
        elif classe == 'akashi':
            vitrine_class.image = 'girar/absoluto.png'
        elif classe == 'aomine':
            vitrine_class.image = 'girar/pantera.png'
        elif classe == 'murasakibara':
            vitrine_class.image = 'girar/muralha.png'

    global rastros_jogador

    for rastro in rastros_jogador:
        rastro["tempo"] -= dt
    rastros_jogador = [
        rastro for rastro in rastros_jogador
        if rastro["tempo"] > 0
    ]           
    if mode == 'game':
        
        tempo_de_jogo -= dt
        if tempo_de_jogo <= 0:
            tempo_de_jogo = 0
            tempo_de_jogo_regride = False
            # Aqui você pode adicionar lógica para finalizar o jogo, mostrar placar, etc.
            '''if pontotime1 > pontotime2:
                print("Time 1 vence!")
            elif pontotime2 > pontotime1:
                print("Time 2 vence!")
            else:
                print("Empate!")'''
        if not bot_moggado_por_akashi:
            if oponente.colliderect(ball) and not drible: # BOT
                posse = 'oponente' #ele corre até a cesta do adversário
                ball.x = oponente.x - 30
                ball.y = oponente.y
                if sexta2.x > oponente.x:
                    oponente.x += 220 * dt
                    oponente._surf = oponente._orig_surf
                elif sexta2.x < oponente.x:
                    oponente.x -= 220 * dt
                    oponente._surf = pygame.transform.flip(oponente._orig_surf, True, False)
                if sexta2.y > oponente.y:
                    oponente.y += 220 * dt
                elif sexta2.y < oponente.y:
                    oponente.y -= 220 * dt
            else:
                if ball_pegou == True and kuroko_invisible == False: # E O KUROKO ESTÁ VISÍVEL
                    if oponente.x > ball.x - 30: # BOT
                        oponente.x -= 250 * dt
                        oponente._surf = pygame.transform.flip(oponente._orig_surf, True, False)
                    elif oponente.x < ball.x + 30:
                        oponente.x += 250 * dt
                        oponente._surf = oponente._orig_surf
                    if oponente.y > ball.y:
                        oponente.y -= 250 * dt
                    if oponente.y < ball.y:
                        oponente.y += 250 * dt

        #KAGAMI
        
        if kagami_ate_cesta:
            tempo_skill += dt

            if kuroko.x < sexta.x:
                kuroko.x += 10
            elif kuroko.x > sexta.x:
                kuroko.x -= 10

            if abs(kuroko.y - sexta.y) > 10:
                if kuroko.y < sexta.y:
                    kuroko.y += 10
                elif kuroko.y > sexta.y:
                    kuroko.y -= 10

            ball.x = kuroko.x
            ball.y = kuroko.y

            if tempo_skill >= 0.7:
                kagami_ate_cesta = False
                tempo_skill = 0
        if kagami_defesa:
            tempo_skill += dt

            if kuroko.x < ball.x:
                kuroko.x += 10
            elif kuroko.x > ball.x:
                kuroko.x -= 10

            if abs(kuroko.y - ball.y) > 10:
                if kuroko.y < ball.y:
                    kuroko.y += 10
                elif kuroko.y > ball.y:
                    kuroko.y -= 10
            if tempo_skill >= 0.7:
                kagami_defesa = False
                tempo_skill = 0
    # Diminuir cooldown da habilidade 1
    if ability1_cooldown > 0:
        ability1_cooldown -= dt
    
    if ability2_cooldown > 0:
        ability2_cooldown -= dt
    if drible_cooldown > 0:
        drible_cooldown -= dt
    

    schedule.run_pending()

    if ball_pegou == True:
        if classe == 'kuroko':
            if mode == "game" and abs(kuroko.y - sexta.y) < 200 and abs(kuroko.x - sexta.x) < 200  and ball_pegou == True:
                ability1_button.image = 'habilidadekuroko1variantepertodacesta.png' #passe fantasma (no despertar é o tornado passe)
            else:
                ability1_button.image = 'habilidadekuroko1.png' #passe fantasma (no despertar é o tornado passe)
            ability2_button.image = 'habilidadekuroko2.png' #fica invisível
        elif classe == 'kise':
            ability1_button.image = 'habilidadekise1.png' #copia habilidade
            ability2_button.image = 'habilidadekise2.png' #copia velocidade, velocidade do passe, stamina, etc
        elif classe == 'kagami':
            ability1_button.image = 'habilidadekagami1.png' #acompanha o oponente mais próximo
            ability2_button.image = 'habilidadekagami2.png' #salta para enterrada
        elif classe == 'midorima':
            ability1_button.image = 'habilidademidorima1.png' #acerta 100% o arremesso, mas quanto mais longe mais demora para arremessar, podendo ser bloqueado
            ability2_button.image = 'habilidademidorima2.png' #aumenta stamina por um tempo
        elif classe == 'akashi':
            ability1_button.image = 'habilidadeakashi1.png' #Faz oponente cair no chão
            ability2_button.image = 'habilidadeakashi2.png' #passa rápido por oponentes
        elif classe == 'aomine':
            ability1_button.image = 'habilidadeaomine1.png' #passa por oponentes 
            ability2_button.image = 'habilidadeaomine2.png' #enterra se tiver perto do fim da quadra
        elif classe == 'murasakibara':
            ability1_button.image = 'habilidademurasakibara1.png'
            ability2_button.image = 'habilidademurasakibara2.png' 
    elif ball_pegou == False:
        if classe == 'kuroko':
            ability1_button.image = 'habilidadekurokovarianteparado1.png' 
            ability2_button.image = 'habilidadekurokovarianteparado2.png' 
        elif classe == 'kise':
            pass
        elif classe == 'kagami':
            pass
        elif classe == 'midorima':
            ability1_button.image = 'habilidademidorima1.png' #acerta 100% o arremesso, mas quanto mais longe mais demora para arremessar, podendo ser bloqueado
            ability2_button.image = 'habilidademidorima2.png' #aumenta stamina por um tempo
        elif classe == 'akashi':
            ability1_button.image = 'habilidadeakashivarianteparado1.png'
            ability2_button.image = 'habilidadeakashivarianteparado2.png'
        elif classe == 'aomine':
            pass
        elif classe == 'murasakibara':
            ability1_button.image = 'habilidademurasakibaravarianteparado1.png'
            ability2_button.image = 'habilidademurasakibaravarianteparado2.png'
    
    # Animação da bola
    if not ball_pegou and not ball_arremessada:
        ball_animation_timer += dt
        if ball_animation_timer >= ball_frame_time:
            ball_animation_frame = (ball_animation_frame + 1) % 10
            ball.image = f'ball_0{ball_animation_frame}.png'
            ball_animation_timer = 0
    #SEXTA
    if ball.colliderect(sexta) and mode == 'game':
        pontotime1 += 1
        arremesso_especial = 0  # Desabilitar efeito após cesta
        oponente.x = 1000
        oponente.y = HEIGHT/2
        kuroko.x = 400
        kuroko.y = 300
        ball.x = WIDTH / 2
        ball.y = HEIGHT / 2
        ball_arremessada = False
        ball_pegou = False
    elif ball.colliderect(sexta2) and mode == 'game':
        pontotime2 += 1
        arremesso_especial = 0  # Desabilitar efeito após cesta
        oponente.x = 1000
        oponente.y = HEIGHT/2
        kuroko.x = 400
        kuroko.y = 300
        ball.x = WIDTH / 2
        ball.y = HEIGHT / 2
        ball_arremessada = False
        ball_pegou = False
        


    # Gerenciamento de stamina
    correndo = keyboard.lshift or keyboard.rshift
    if correndo and stamina > 0:
        if classe == 'kuroko':
            velocidade = 400  # pixels por segundo
            stamina -= 50 * dt  # Diminui stamina ao correr
            if stamina < 0:
                stamina = 0
        elif classe == 'kise':
            velocidade = 480  # pixels por segundo
            stamina -= 55 * dt  # Diminui stamina ao correr
            if stamina < 0:
                stamina = 0
        elif classe == 'kagami':
            velocidade = 420  # pixels por segundo
            stamina -= 40 * dt  # Diminui stamina ao correr
            if stamina < 0:
                stamina = 0
        elif classe == 'midorima':
            velocidade = 400  # pixels por segundo
            stamina -= 30 * dt  # Diminui stamina ao correr
            if stamina < 0:
                stamina = 0
        elif classe == 'akashi':
            velocidade = 420  # pixels por segundo
            stamina -= 45 * dt  # Diminui stamina ao correr
            if stamina < 0:
                stamina = 0
        elif classe == 'aomine':
            if aomine_drible:
                velocidade = 600  # Aumenta a velocidade durante o drible do Aomine
                stamina -= 0 * dt  # Diminui stamina ao correr
                if stamina < 0:
                    stamina = 0
            else:
                velocidade = 490  # pixels por segundo
                stamina -= 50 * dt  # Diminui stamina ao correr
                if stamina < 0:
                    stamina = 0
        elif classe == 'murasakibara':
            velocidade = 400  # pixels por segundo
            stamina -= 35 * dt  # Diminui stamina ao correr
            if stamina < 0:
                stamina = 0
    else:
        if classe == 'kuroko':
            velocidade = 200  # pixels por segundo
            if not correndo:
                stamina += 20 * dt  # Recarrega stamina quando não correndo
        elif classe == 'kise':
            velocidade = 200  # pixels por segundo
            if not correndo:
                stamina += 20 * dt  # Recarrega stamina quando não correndo
        elif classe == 'kagami':
            velocidade = 210  # pixels por segundo
            if not correndo:
                stamina += 20 * dt  # Recarrega stamina quando não correndo
        elif classe == 'midorima':
            velocidade = 200  # pixels por segundo
            if not correndo:
                stamina += 30 * dt  # Recarrega stamina quando não correndo
        elif classe == 'akashi':
            velocidade = 200  # pixels por segundo
            if not correndo:
                stamina += 20 * dt  # Recarrega stamina quando não correndo
        elif classe == 'aomine':
            if aomine_drible:
                velocidade = 600  # pixels por segundo
                if not correndo:
                    stamina += 20 * dt  # Recarrega stamina quando não correndo
            else:
                velocidade = 220  # pixels por segundo
                if not correndo:
                    stamina += 30 * dt  # Recarrega stamina quando não correndo
        elif classe == 'murasakibara':
            velocidade = 210  # pixels por segundo
            if not correndo:
                stamina += 25 * dt  # Recarrega stamina quando não correndo
        if stamina > 100:
            stamina = 100

    if not moggado_por_akashi:    
        if keyboard.w:
            kuroko.y -= velocidade * dt
        if keyboard.s:
            kuroko.y += velocidade * dt
        if keyboard.a:
            kuroko.x -= velocidade * dt
        if keyboard.d:
            kuroko.x += velocidade * dt
   

    # Limites da tela para evitar sair da quadra
    kuroko.x = max(0, min(WIDTH, kuroko.x))
    kuroko.y = max(0, min(HEIGHT, kuroko.y))
    
    # Lógica da bola
    if ball_arremessada:
        # Arremesso do Midorima (sempre especial quando usado)
        if arremesso_especial == 1: #RÁPIDO
            velocidade_bola = 1000
            ball.x += ball_dx * velocidade_bola * dt
            ball.y += ball_dy * velocidade_bola * dt
        elif arremesso_especial == 0:#NORMAL
            velocidade_bola = 500
            ball.x += ball_dx * velocidade_bola * dt
            ball.y += ball_dy * velocidade_bola * dt
        elif arremesso_especial == 2:#KAGAMI
            ax = 0
            ball_pegou = False
            schedule.clear('arremesso_kagami')  # Limpa qualquer rastro anterior
            def arremessoa():
                global ax, ball_pegou, arremesso_especial
                if ball_arremessada != False and arremesso_especial == 2:
                    ball.x += 10
                    ball.y += 2
                    ax += 1


                if ax >= 100:  # Se sair da tela, para de criar rastros
                    
                    return schedule.CancelJob

            schedule.every(0.001).seconds.do(arremessoa).tag('arremesso_kagami')  # Cria rastro a cada 0.1 segundos
        elif arremesso_especial == 3:#MIDORIMA
            tempo_arremesso += dt

            gravidade = 400
            velocidade_inicial = -500
            velocidade_bola = 300
            rastros_bola.append((ball.x, ball.y))

            # Limita o tamanho do rastro
            if len(rastros_bola) > 15:
                rastros_bola.pop(0)

            # Movimento horizontal
            ball.x += ball_dx * velocidade_bola * dt

            # Movimento vertical da parábola
            velocidade_y = velocidade_inicial + gravidade * tempo_arremesso
            ball.y += velocidade_y * dt
        elif arremesso_especial == 4:#Kuroko
            tempo_arremesso += dt

            gravidade = 600
            velocidade_inicial = -700
            velocidade_bola = 20
            rastros_bola.append((ball.x, ball.y))

            # Limita o tamanho do rastro
            if len(rastros_bola) > 15:
                rastros_bola.pop(0)

            # Movimento horizontal
            ball.x += ball_dx * velocidade_bola * dt

            # Movimento vertical da parábola
            velocidade_y = velocidade_inicial + gravidade * tempo_arremesso
            ball.y += velocidade_y * dt
        elif arremesso_especial == 5:#Aomine
            tempo_arremesso += dt

            gravidade = 600
            velocidade_inicial = -700
            velocidade_bola = 30
            rastros_bola.append((ball.x, ball.y))

            # Limita o tamanho do rastro
            if len(rastros_bola) > 15:
                rastros_bola.pop(0)

            # Movimento horizontal
            ball.x += ball_dx * velocidade_bola * dt

            # Movimento vertical da parábola
            velocidade_y = velocidade_inicial + gravidade * tempo_arremesso
            ball.y += velocidade_y * dt








        # Verificar colisão com cestas durante arremesso
        if ball.colliderect(sexta) and mode == 'game':
            pontotime1 += 1
            arremesso_especial = 0  # Desabilitar efeito após cesta
            oponente.x = 1000
            oponente.y = HEIGHT/2
            kuroko.x = 400
            kuroko.y = 300
            ball.x = WIDTH / 2
            ball.y = HEIGHT / 2
            ball_arremessada = False
            ball_pegou = False
            rastros_bola = []
        elif ball.colliderect(sexta2) and mode == 'game':
            pontotime2 += 1
            arremesso_especial = 0  # Desabilitar efeito após cesta
            oponente.x = 1000
            oponente.y = HEIGHT/2
            kuroko.x = 400
            kuroko.y = 300
            ball.x = WIDTH / 2
            ball.y = HEIGHT / 2
            ball_arremessada = False
            ball_pegou = False
            rastros_bola = []
        elif ball.colliderect(oponente) and mode == 'game':
            posse = 'oponente'
            ball_arremessada = False
            ball_pegou = False
            
        # Resetar se sair da tela
        elif ball.x < 0 or ball.x > WIDTH or ball.y < 0 or ball.y > HEIGHT:
            ball.x = WIDTH / 2
            ball.y = HEIGHT / 2
            oponente.x = 1000
            oponente.y = HEIGHT/2
            ball_arremessada = False
            ball_pegou = False
            arremesso_especial = 0
            rastros_bola = []
    elif ball.colliderect(kuroko):
        posse = 'player1'
        ball_pegou = True
        ball.x = kuroko.x + 30
        ball.y = kuroko.y
    elif not ball.colliderect(kuroko) and not ball_arremessada:
        ball_pegou = False
        



pgzrun.go()