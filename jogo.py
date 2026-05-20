import pgzrun, random, os
import pygame
from pgzero.actor import Actor
import schedule
from pgzero.rect import Rect

"""if os.path.exists('jogo/save.txt'):
                    carregar_jogo() 
                else:
                    mode = 'intro' # COLOCAR INTRO DEPOIS"""

# IDEIA : FAZER LISTA TIME 1 e 2, Se boneco tal tocar no time 2 (vale pra qualquer elemento) rouba a bola (dai n precisa fzr interação com todos)
quadra = Actor('quadra.jpg')

tempo_de_jogo = 300  # Tempo de jogo em segundos (5 minutos)
tempo_de_jogo_regride = False

mode = 'lobby'

WIDTH = quadra.width
HEIGHT = quadra.height
TITLE = "Kuroko no Basket" # Título do jogo
FPS = 60 # Quadros por segundo

despertar = False
posse = 'empty'

pontotime1 = 0
pontotime2 = 0
level = 1
dinheiro = 0
stamina = 100  # Stamina máxima
classe = 'midorima'  # Classe inicial do jogador


kuroko = Actor('kuroko.png', (400, 300))
oponente = Actor('kise.png', (1000, HEIGHT/2))

ability1_button = Actor('habilidadekurokovarianteparado1.png', (WIDTH - 200, HEIGHT - 100))
ability2_button = Actor('habilidadekurokovarianteparado2.png', (WIDTH - 100, HEIGHT - 100))

play = Actor('play.png', center=(WIDTH/2, HEIGHT-100))

ball = Actor('ball_00.png', center=(WIDTH/2, HEIGHT/2), size=(30,55555))

sexta = Actor('sextateste.png', (WIDTH - 160, HEIGHT/2))

sexta2 = Actor('sextateste.png', (160, HEIGHT/2))
sexta2._surf = pygame.transform.flip(sexta2._orig_surf, True, False)

arremesso_especial = 0
kuroko_invisible = False
spin_button = Actor('spin.png', (100, HEIGHT - 100))
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

# Curva parabólica do MIDORIMA-----------------
# Removido - habilidade simplificada para apenas arremesso rápido

# Hold do C para MIDORIMA------------------
# Removido - habilidade simplificada para apenas arremesso rápido






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



def parabola(x):
    x*x*-1+x*2+5

def spin():
    global dinheiro, classe
    #giro da sorte dps
    a =random.randint(1,100)
    if a == 100:
        classe = 'Aomine'
        #AOI (TENDA)
    elif a > 1 and a <=25:
        classe = 'kuroko'
        #kuroko (sombra) 
    elif a >25 and a <=50:
        classe = 'kise'
        #kise (copia)
    elif a >50 and a <=75:
        classe = 'kagami'
        #Kagami (dragão)
    elif a >75 and a <100:
        classe = 'midorima'
        #Midorima (tiro de 3)
    elif a == 1:
        classe = 'akashi'
        #Akashi (capitão)


    

def draw():
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


    elif mode == 'game':
        screen.clear()
        quadra.draw()
        kuroko.draw()
        oponente.draw()
        ball.draw()
        sexta.draw()
        sexta2.draw()

        
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


def on_key_down(key):
    global stamina, kuroko_invisible, posse, ball_arremessada, ball_dx, ball_dy, ball_pegou, ability1_cooldown, ability2_cooldown, despertar, arremesso_especial
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
                        pass  # Habilidade 1 do Kagami
                    elif classe == 'midorima':
                        pass  # Habilidade 1 do Midorima
                    elif classe == 'akashi':
                        pass  # Habilidade 1 do Akashi
                    elif classe == 'aomine':
                        pass  # Habilidade 1 do Aomine
            elif ball_pegou == True: # variante COM A BOLA
                if classe == 'kuroko':
                    pass # Habilidade 1 do Kuroko com a bola
                    #TERIA Q TER O ONLINE PARA FZR ESSA HABILIDADE COM A BOLA
                    #HABILIDADE: PASSE FANTASMA
                    #Referência: https://www.youtube.com/watch?v=jWVe02jgGLM
                    #minutagem: 1:15 até 1:20

                elif classe == 'kise':     
                    pass  # Habilidade 1 do Kise
                elif classe == 'kagami':
                    pass  # Habilidade 1 do Kagami
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
                        arremesso_especial = 1
                        ball_arremessada = True
                        ball_pegou = False

                elif classe == 'akashi':
                    pass  # Habilidade 1 do Akashi
                elif classe == 'aomine':
                    pass  # Habilidade 1 do Aomine
            
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
                    elif classe == 'kagami':
                        pass  # Habilidade 2 do Kagami
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
                    pass # PARA A HABILIDADE DE DRIBLE COM A BOLA PRECISO DE OUTRO PLAYER PARA A CUTSCIENE ENT N DA PRA FZR AGR
                    #HABILIDADE : DRIBLE DAS SOMBRAS
                    #Referência: https://www.youtube.com/shorts/wLZ6f_yZyf0
                    
                elif classe == 'kise':
                    pass  # Habilidade 2 do Kise
                elif classe == 'kagami':
                    pass  # Habilidade 2 do Kagami
                elif classe == 'midorima':
                    pass  # Habilidade 2 do Midorima
                elif classe == 'akashi':
                    pass  # Habilidade 2 do Akashi
                elif classe == 'aomine':
                    pass  # Habilidade 2 do Aomine

                    
                    
                # kuroko dá um dash rápido para onde estiver olhando

            elif classe == 'kise':
                pass  # Habilidade 2 do Kise
            elif classe == 'kagami':
                pass  # Habilidade 2 do Kagami
            elif classe == 'midorima':
                pass  # Habilidade 2 do Midorima
            elif classe == 'akashi':
                pass  # Habilidade 2 do Akashi
            elif classe == 'aomine':
                pass  # Habilidade 2 do Aomine
    elif despertar == True: # se já tiver despertado, HABILIDADES DESPERTAR
        pass # implementar habilidades de despertar depois

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
            pass
        kuroko._surf.set_alpha(alpha)  # Restaurar opacidade

    if key == keys.SPACE and ball_pegou:
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
    global mode, pontotime1, pontotime2, tempo_de_jogo, tempo_de_jogo_regride
    if button == mouse.LEFT:
        if mode == 'lobby' and spin_button.collidepoint(pos):
            spin()
        if mode == 'lobby' and play.collidepoint(pos):
            mode = 'game'
            pontotime2 = 0
            pontotime1 = 0
            tempo_de_jogo = 300  # Reinicia o tempo de jogo ao começar
            tempo_de_jogo_regride = True


def update(dt):
    global kuroko_invisible, posse, tempo_de_jogo, tempo_de_jogo_regride,stamina, ball_pegou, ball_arremessada, pontotime1, ball_animation_timer, ball_animation_frame, ability1_cooldown, ability2_cooldown, pontotime2, arremesso_especial, ball_dx, ball_dy
    
    if mode == 'game' and tempo_de_jogo_regride:
        
        tempo_de_jogo -= dt
        if tempo_de_jogo <= 0:
            tempo_de_jogo = 0
            tempo_de_jogo_regride = False
            # Aqui você pode adicionar lógica para finalizar o jogo, mostrar placar, etc.
            if pontotime1 > pontotime2:
                print("Time 1 vence!")
            elif pontotime2 > pontotime1:
                print("Time 2 vence!")
            else:
                print("Empate!")

        if oponente.colliderect(ball): # BOT
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
        

    # Diminuir cooldown da habilidade 1
    if ability1_cooldown > 0:
        ability1_cooldown -= dt
    
    if ability2_cooldown > 0:
        ability2_cooldown -= dt

    

    schedule.run_pending()
    if ball_pegou == True:
        if classe == 'kuroko':
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
            pass
        elif classe == 'aomine':
            pass
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
        

    #adicionar para outro time se for outra sexta

    # Gerenciamento de stamina
    correndo = keyboard.lshift or keyboard.rshift
    if correndo and stamina > 0:
        velocidade = 400  # pixels por segundo
        stamina -= 50 * dt  # Diminui stamina ao correr
        if stamina < 0:
            stamina = 0
    else:
        velocidade = 200  # pixels por segundo
        if not correndo:
            stamina += 20 * dt  # Recarrega stamina quando não correndo
            if stamina > 100:
                stamina = 100
    
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
        if arremesso_especial == 1:
            velocidade_bola = 1000
        elif arremesso_especial == 0:
            velocidade_bola = 500
        ball.x += ball_dx * velocidade_bola * dt
        ball.y += ball_dy * velocidade_bola * dt
        
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
        
    elif ball.colliderect(kuroko):
        posse = 'player1'
        ball_pegou = True
        ball.x = kuroko.x + 30
        ball.y = kuroko.y
    elif not ball.colliderect(kuroko) and not ball_arremessada:
        ball_pegou = False
        



pgzrun.go()