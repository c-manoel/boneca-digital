"""Visualizador independente do personagem 3D usando Panda3D.

Execute com: python boneca_3d.py
Teclas: 1 idle, 2 walk, 3 run, 4 wave, 5 jump, R reinicia idle, Esc fecha.
"""
from pathlib import Path

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4, WindowProperties


MODEL_PATH = Path(__file__).parent / "assets" / "boneca_3d" / "grab3d-lowpoly-character.glb"
ANIMATION_KEYS = {
    "1": "idle",
    "2": "walk",
    "3": "run",
    "4": "wave",
    "5": "jump",
}


class Boneca3D(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0.91, 0.92, 0.93, 1)
        self.disableMouse()
        propriedades = WindowProperties()
        propriedades.setTitle("Boneca Digital — visualizador 3D")
        self.win.requestProperties(propriedades)

        if not MODEL_PATH.is_file():
            raise FileNotFoundError(f"Modelo 3D não encontrado: {MODEL_PATH}")

        # O import registra o suporte GLTF/GLB no loader do Panda3D.
        import gltf  # noqa: F401

        self.boneca = Actor(str(MODEL_PATH))
        self.boneca.reparentTo(self.render)
        self._fit_model()

        ambient = AmbientLight("luz-ambiente")
        ambient.setColor(Vec4(0.72, 0.72, 0.76, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        key = DirectionalLight("luz-principal")
        key.setColor(Vec4(0.95, 0.91, 0.84, 1))
        key_np = self.render.attachNewNode(key)
        key_np.setHpr(-35, -45, 0)
        self.render.setLight(key_np)

        self.camera.setPos(0, -4.2, 1.05)
        self.camera.lookAt(0, 0, 0.9)

        self.animacoes = {name.lower(): name for name in self.boneca.getAnimNames()}
        print("Animações encontradas:", list(self.animacoes.values()))
        if "idle" in self.animacoes:
            self.tocar("idle")

        for tecla, nome in ANIMATION_KEYS.items():
            self.accept(tecla, self.tocar, [nome])
        self.accept("r", self.tocar, ["idle"])
        self.accept("escape", self.userExit)

    def _fit_model(self):
        """Centraliza e dimensiona o personagem a partir dos limites do modelo."""
        bounds = self.boneca.getTightBounds()
        if not bounds:
            self.boneca.setScale(1)
            return
        minimum, maximum = bounds
        center = (minimum + maximum) * 0.5
        height = maximum.z - minimum.z
        if height > 0:
            self.boneca.setScale(1.8 / height)
        self.boneca.setPos(-center.x, -center.y, -minimum.z)

    def tocar(self, nome):
        nome_real = self.animacoes.get(nome.lower())
        if not nome_real:
            print(f"Animação '{nome}' não encontrada. Disponíveis: {list(self.animacoes.values())}")
            return
        self.boneca.loop(nome_real)
        print(f"Reproduzindo: {nome_real}")


if __name__ == "__main__":
    app = Boneca3D()
    app.run()
