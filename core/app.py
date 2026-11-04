"""Aplicação demonstrativa da Boneca Digital, feita inteiramente com Panda3D."""
from pathlib import Path

from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    BitMask32,
    CollisionHandlerQueue,
    CollisionNode,
    CollisionRay,
    CollisionSphere,
    CollisionTraverser,
    DirectionalLight,
    TextNode,
    Vec4,
    loadPrcFileData,
)


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "boneca_3d" / "grab3d-lowpoly-character.glb"


class BonecaApp(ShowBase):
    """Interface touch-first com Panda3D como único sistema gráfico."""

    def __init__(self):
        # Valores visuais para desktop. O setup.py seleciona pandagles2 no Android.
        loadPrcFileData("boneca-digital", "window-title Minha Amiga - Boneca Digital")
        loadPrcFileData("boneca-digital", "win-size 720 1280")
        loadPrcFileData("boneca-digital", "audio-library-name null")
        super().__init__()

        self.setBackgroundColor(247 / 255, 244 / 255, 237 / 255, 1)
        self.disableMouse()
        self.widgets = []
        self.current_screen = "home"
        self.selected_mood = None
        self.selected_region = None
        self.selection_marker = None

        if not MODEL_PATH.is_file():
            raise FileNotFoundError(f"Modelo 3D não encontrado: {MODEL_PATH}")

        # Registra o carregador GLB do pacote panda3d-gltf.
        import gltf  # noqa: F401

        self.character = Actor(str(MODEL_PATH))
        self.character.reparentTo(self.render)
        self._fit_character()
        self._add_lighting()
        self._setup_camera()
        self._start_idle_animation()
        self._setup_body_picker()

        # mouse1 também é emitido para toques na maioria dos dispositivos Panda3D.
        self.accept("mouse1", self._on_body_touch)
        self.accept("escape", self.userExit)
        self.show_screen("home")

    def _fit_character(self):
        bounds = self.character.getTightBounds()
        if not bounds:
            self.character.setScale(1)
            return
        minimum, maximum = bounds
        center = (minimum + maximum) * 0.5
        height = maximum.z - minimum.z
        if height > 0:
            self.character.setScale(1.8 / height)
        self.character.setPos(-center.x, -center.y, -minimum.z)

    def _add_lighting(self):
        ambient = AmbientLight("luz-ambiente")
        ambient.setColor(Vec4(0.72, 0.72, 0.76, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        key = DirectionalLight("luz-principal")
        key.setColor(Vec4(0.95, 0.92, 0.86, 1))
        key_np = self.render.attachNewNode(key)
        key_np.setHpr(-35, -45, 0)
        self.render.setLight(key_np)

    def _setup_camera(self):
        self.camera.setPos(0, -4.2, 1.05)
        self.camera.lookAt(0, 0, 0.9)

    def _start_idle_animation(self):
        self.animations = {name.lower(): name for name in self.character.getAnimNames()}
        idle = self.animations.get("idle")
        if idle:
            self.character.loop(idle)

    def _setup_body_picker(self):
        self.pick_queue = CollisionHandlerQueue()
        self.picker = CollisionTraverser("body-picker")

        ray = CollisionRay()
        ray_node = CollisionNode("body-pick-ray")
        ray_node.addSolid(ray)
        ray_node.setFromCollideMask(BitMask32.bit(1))
        ray_node.setIntoCollideMask(BitMask32.allOff())
        self.ray_np = self.camera.attachNewNode(ray_node)
        self.picker.addCollider(self.ray_np, self.pick_queue)

        # Áreas aproximadas no espaço do modelo já centralizado e escalado.
        # Os raios precisam ser ajustados visualmente para este personagem.
        regions = [
            ("cabeça", 0.00, 0.0, 1.62, 0.17),
            ("tronco", 0.00, 0.0, 1.13, 0.27),
            ("braço esquerdo", -0.34, 0.0, 1.12, 0.16),
            ("braço direito", 0.34, 0.0, 1.12, 0.16),
            ("perna esquerda", -0.13, 0.0, 0.48, 0.15),
            ("perna direita", 0.13, 0.0, 0.48, 0.15),
        ]
        self.hit_regions = []
        for name, x, y, z, radius in regions:
            node = CollisionNode(f"region:{name}")
            node.addSolid(CollisionSphere(0, 0, 0, radius))
            node.setFromCollideMask(BitMask32.allOff())
            node.setIntoCollideMask(BitMask32.bit(1))
            path = self.render.attachNewNode(node)
            path.setPos(x, y, z)
            self.hit_regions.append(path)

    def clear_widgets(self):
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def _label(self, text, y, scale=0.075, color=(0.20, 0.26, 0.28, 1), wordwrap=15):
        label = DirectLabel(
            parent=self.aspect2d,
            text=text,
            text_align=TextNode.ACenter,
            text_fg=color,
            text_scale=scale,
            text_wordwrap=wordwrap,
            frameColor=(1, 1, 1, 0),
            pos=(0, 0, y),
        )
        self.widgets.append(label)
        return label

    def _button(self, text, y, command, color=(0.24, 0.56, 0.53, 1), x=0, compact=False):
        # Escala relativa à largura: os botões permanecem dentro da tela em retrato.
        aspect = max(0.45, self.getAspectRatio())
        scale = min(0.115, aspect * (0.065 if compact else 0.14))
        half_width = 3.7 if compact else 4.0
        button = DirectButton(
            parent=self.aspect2d,
            text=text,
            text_align=TextNode.ACenter,
            text_scale=0.55,
            text_fg=(1, 1, 1, 1),
            text_wordwrap=14,
            frameSize=(-half_width, half_width, -0.98, 0.98),
            frameColor=(color, color, (color[0] * 0.88, color[1] * 0.88, color[2] * 0.88, 1), color),
            relief=1,
            borderWidth=(0.02, 0.02),
            scale = min(0.215, aspect * (0.1 if compact else 0.14)),
            pos=(x, 0, y),
            command=command,
        )
        self.widgets.append(button)
        return button

    def show_screen(self, name):
        self.clear_widgets()
        if self.selection_marker is not None:
            self.selection_marker.destroy()
            self.selection_marker = None
        self.current_screen = name
        self.selected_region = None
        self.character.show()

        if name == "home":
            self._label("MINHA AMIGA", 1.12, 0.09, (0.24, 0.56, 0.53, 1))
            self._label("Uma boneca digital para acompanhar você", 1.06, 0.045)
            self._button("COMEÇAR", -0.98, lambda: self.show_screen("intro"))

        elif name == "intro":
            self._label("Oi! Eu sou sua amiga.", 1.12, 0.075, (0.24, 0.56, 0.53, 1))
            self._label("Vamos explorar juntinhas?", 1.02, 0.05)    
            self._label("Toque nos botões para continuar.", 0.92, 0.04)
            self._button("VOLTAR", -0.98, lambda: self.show_screen("home"), (0.70, 0.66, 0.82, 1), x=-0.34, compact=True)
            self._button("CONTINUAR", -0.98, lambda: self.show_screen("mood"), (0.90, 0.48, 0.41, 1), x=0.34, compact=True)

        elif name == "mood":
            self.character.hide()
            self._label("COMO VOCÊ ESTÁ?", 0.83, 0.075, (0.24, 0.56, 0.53, 1))
            self._label("Escolha uma opção", 0.69, 0.045)
            choices = [
                ("FELIZ", (0.95, 0.75, 0.30, 1), "😊"),
                ("BEM", (0.39, 0.70, 0.66, 1), "🙂"),
                ("PREOCUPADO", (0.72, 0.68, 0.84, 1), "😕"),
                ("TRISTE", (0.53, 0.73, 0.83, 1), "😢"),
                ("DESCONFORTÁVEL", (0.91, 0.56, 0.49, 1), "🤢"),
            ]
            for index, (choice, color, icon_nome) in enumerate(choices):
                y = 0.45 - index * 0.21

                self._button(
                    f"{icon_nome} {choice}",
                    y,
                    lambda c=choice: self._select_mood(c),
                    color,
                    compact=True

                )
                self._button(choice, y, lambda c=choice: self._select_mood(c), color)
            self.mood_label = self._label("Toque em uma opção", -0.60, 0.04)
            self._button("VOLTAR", -0.82, lambda: self.show_screen("intro"), (0.70, 0.66, 0.82, 1), x=-0.34, compact=True)
            self._button("CONTINUAR", -0.82, self._continue_mood, (0.24, 0.56, 0.53, 1), x=0.34, compact=True)

        elif name == "body":
            self._label("ONDE VOCÊ SENTE DOR?", 1.04, 0.065, (0.24, 0.56, 0.53, 1))
            self._label("Toque em uma parte da boneca", 0.92, 0.043)
            self.region_label = self._label("Nenhuma região selecionada", -0.94, 0.043)
            self._button("VOLTAR", -1.12, lambda: self.show_screen("mood"), (0.70, 0.66, 0.82, 1), x=-0.34, compact=True)
            self._button("ENCERRAR", -1.12, lambda: self.show_screen("end"), (0.24, 0.56, 0.53, 1), x=0.34, compact=True)

        elif name == "end":
            self._label("OBRIGADA POR ME CONTAR!", 1.02, 0.065, (0.24, 0.56, 0.53, 1))
            self._label("Você pode voltar ao início quando quiser.", 0.97, 0.043)
            self._button("VOLTAR AO INÍCIO", -1.02, lambda: self.show_screen("home"))

    def _select_mood(self, choice):
        # O protótipo apenas registra visualmente a escolha; não a interpreta.
        self.selected_mood = choice
        self.mood_label["text"] = f"Você escolheu: {choice}"

    def _continue_mood(self):
        if self.selected_mood is not None:
            self.show_screen("body")
        else:
            self.mood_label["text"] = "Toque em uma opção para continuar"

    def _on_body_touch(self):
        if self.current_screen != "body" or not self.mouseWatcherNode.hasMouse():
            return
        mouse = self.mouseWatcherNode.getMouse()
        # Evita tratar toques nos textos e botões como toques no corpo.
        if mouse.y < -0.52 or mouse.y > 0.66:
            return
        ray = self.ray_np.node().modifySolid(0)
        ray.setFromLens(self.camNode, mouse.x, mouse.y)
        self.pick_queue.clearEntries()
        self.picker.traverse(self.render)
        self.pick_queue.sortEntries()
        if not self.pick_queue.getNumEntries():
            return
        node = self.pick_queue.getEntry(0).getIntoNodePath().node()
        if not node.getName().startswith("region:"):
            return
        self.selected_region = node.getName().split(":", 1)[1]
        self.region_label["text"] = f"Você selecionou: {self.selected_region}"
        if self.selection_marker is not None:
            self.selection_marker.destroy()
        self.selection_marker = DirectFrame(
            parent=self.aspect2d,
            frameColor=(0.92, 0.36, 0.29, 0.88),
            frameSize=(-0.025, 0.025, -0.025, 0.025),
            pos=(mouse.x * self.getAspectRatio(), 0, mouse.y),
        )
