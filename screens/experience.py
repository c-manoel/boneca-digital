"""Telas da experiência demonstrativa. As escolhas não são interpretadas."""
import pygame
from config.settings import COLORS
from core.screen import Screen
from core.ui import button, draw_doll, draw_text, panel


class Home(Screen):
    def draw(self):
        super().draw()
        draw_text(self.app.surface, "MINHA AMIGA", 42, COLORS["teal_dark"], (480, 76), True)
        draw_text(self.app.surface, "uma boneca digital para acompanhar você", 19, COLORS["muted"], (480, 112))
        pygame.draw.ellipse(self.app.surface, (235, 229, 211), (350, 485, 260, 25))
        draw_doll(self.app.surface, (480, 344), 1.48, self.app.ticks)
        button(self.app.surface, (350, 530, 260, 68), "COMEÇAR", COLORS["teal_dark"], self.app.mouse)
        draw_text(self.app.surface, "Uma experiência de acolhimento", 15, COLORS["muted"], (480, 616))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(350,530,260,68).collidepoint(event.pos): self.app.show("intro")


class Intro(Screen):
    def draw(self):
        super().draw(); self.heading("Oi! Eu sou sua amiga.", "Estou feliz em conhecer você!")
        panel(self.app.surface, (130,145,700,375))
        pygame.draw.ellipse(self.app.surface, (235,229,211), (205,450,230,20))
        draw_doll(self.app.surface, (320,340), 1.28, self.app.ticks)
        draw_text(self.app.surface, "Vamos explorar juntinhas?", 25, COLORS["ink"], (620,285), True)
        draw_text(self.app.surface, "Você pode tocar nas figuras", 18, COLORS["muted"], (620,324))
        draw_text(self.app.surface, "e escolher o que quiser.", 18, COLORS["muted"], (620,352))
        button(self.app.surface,(535,410,190,60),"CONTINUAR",COLORS["coral"],self.app.mouse,20)
        button(self.app.surface,(42,555,145,52),"VOLTAR",COLORS["lavender"],self.app.mouse,18)

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if pygame.Rect(535,410,190,60).collidepoint(event.pos): self.app.show("mood")
            elif pygame.Rect(42,555,145,52).collidepoint(event.pos): self.app.show("home")


class Mood(Screen):
    choices = [("Feliz","☺",COLORS["yellow"]),("Bem","○",COLORS["teal"]),("Preocupado","？",COLORS["lavender"]),("Triste","☹",COLORS["blue"]),("Desconfortável","…",COLORS["coral"])]
    def __init__(self,app): super().__init__(app); self.selected=None
    def draw(self):
        super().draw(); self.heading("Como você está?", "Escolha uma carinha — não existe resposta certa.")
        card_w, gap = 145, 22
        start = (960 - (5*card_w+4*gap))//2
        for i,(label,face,color) in enumerate(self.choices):
            x=start+i*(card_w+gap); rect=pygame.Rect(x,220,card_w,205)
            panel(self.app.surface,rect, (255,255,255))
            if i==self.selected:
                pygame.draw.rect(self.app.surface,COLORS["teal_dark"],rect,4,border_radius=28)
            pygame.draw.circle(self.app.surface,color,(x+card_w//2,290),48)
            draw_text(self.app.surface,face,62,COLORS["ink"],(x+card_w//2,291),True)
            draw_text(self.app.surface,label,16,COLORS["ink"],(x+card_w//2,365),True)
        button(self.app.surface,(42,555,145,52),"VOLTAR",COLORS["lavender"],self.app.mouse,18)
        button(self.app.surface,(713,555,205,52),"CONTINUAR",COLORS["teal_dark"],self.app.mouse,18)
        if self.selected is not None:
            draw_text(self.app.surface,"Obrigada por me contar!",19,COLORS["muted"],(480,480))

    def handle_event(self,event):
        if event.type!=pygame.MOUSEBUTTONDOWN or event.button!=1: return
        card_w,gap=145,22; start=(960-(5*card_w+4*gap))//2
        for i in range(5):
            if pygame.Rect(start+i*(card_w+gap),220,card_w,205).collidepoint(event.pos): self.selected=i
        if pygame.Rect(42,555,145,52).collidepoint(event.pos): self.app.show("intro")
        elif pygame.Rect(713,555,205,52).collidepoint(event.pos): self.app.show("body")


class Body(Screen):
    # Áreas desenhadas esquematicamente; não representam regiões para diagnóstico.
    zones = [("cabeça",(480,232),(70,72)),("tronco",(480,350),(82,100)),("braço esquerdo",(390,345),(38,94)),("braço direito",(570,345),(38,94)),("perna esquerda",(450,475),(42,95)),("perna direita",(510,475),(42,95))]
    def __init__(self,app): super().__init__(app); self.selected=None
    def draw(self):
        super().draw(); self.heading("Vamos conhecer o corpo", "Toque em uma parte para destacar.")
        # Desenho simplificado e abstrato, feito com formas geométricas.
        for i,(name,(x,y),(rx,ry)) in enumerate(self.zones):
            color=COLORS["coral"] if self.selected==i else COLORS["skin"]
            pygame.draw.ellipse(self.app.surface,color,(x-rx,y-ry,rx*2,ry*2))
            pygame.draw.ellipse(self.app.surface,COLORS["teal_dark"] if self.selected==i else COLORS["white"],(x-rx,y-ry,rx*2,ry*2),4)
        # rosto
        pygame.draw.circle(self.app.surface,COLORS["ink"],(458,229),4); pygame.draw.circle(self.app.surface,COLORS["ink"],(502,229),4)
        pygame.draw.arc(self.app.surface,COLORS["coral"],(465,238,30,20),3.3,6.1,3)
        button(self.app.surface,(42,555,145,52),"VOLTAR",COLORS["lavender"],self.app.mouse,18)
        button(self.app.surface,(713,555,205,52),"ENCERRAR",COLORS["teal_dark"],self.app.mouse,18)
        if self.selected is not None:
            draw_text(self.app.surface,"Você tocou em: "+self.zones[self.selected][0],19,COLORS["muted"],(480,535))

    def handle_event(self,event):
        if event.type!=pygame.MOUSEBUTTONDOWN or event.button!=1: return
        pos=event.pos
        if pygame.Rect(42,555,145,52).collidepoint(pos): self.app.show("mood"); return
        if pygame.Rect(713,555,205,52).collidepoint(pos): self.app.show("end"); return
        for i,(_, (x,y),(rx,ry)) in enumerate(self.zones):
            if ((pos[0]-x)/rx)**2+((pos[1]-y)/ry)**2<=1: self.selected=i; break


class End(Screen):
    def draw(self):
        super().draw(); self.heading("Obrigada por brincar comigo!", "Você pode voltar ao início quando quiser.")
        panel(self.app.surface,(190,150,580,350))
        pygame.draw.ellipse(self.app.surface,(235,229,211),(385,435,190,18))
        draw_doll(self.app.surface,(480,325),1.05,self.app.ticks)
        button(self.app.surface,(350,475,260,62),"VOLTAR AO INÍCIO",COLORS["teal_dark"],self.app.mouse,19)
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and pygame.Rect(350,475,260,62).collidepoint(event.pos): self.app.show("home")
