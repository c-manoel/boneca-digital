"""Protótipo local da Boneca Digital, construído inteiramente com Panda3D."""
from pathlib import Path

from direct.actor.Actor import Actor
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.interval.IntervalGlobal import LerpScaleInterval, Sequence
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    AmbientLight,
    BitMask32,
    CollisionHandlerQueue,
    CollisionNode,
    CollisionRay,
    CollisionSphere,
    CollisionTraverser,
    DirectionalLight,
    Point2,
    Point3,
    TextNode,
    TransparencyAttrib,
    Vec4,
    loadPrcFileData,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "boneca_3d" / "grab3d-lowpoly-character.glb"
UI_ASSETS = ROOT / "assets" / "ui"
SOUND_PATH = ROOT / "assets" / "audio" / "soft_chime.wav"

# Cores escuras o bastante para texto branco; a seleção também usa um X,
# para que a cor nunca seja a única maneira de perceber o estado.
TEAL = (0.10, 0.38, 0.35, 1)
MINT = (0.39, 0.70, 0.66, 1)
BLUE = (0.16, 0.34, 0.52, 1)
PURPLE = (0.38, 0.29, 0.52, 1)
RED = (0.58, 0.25, 0.24, 1)
GOLD = (0.50, 0.35, 0.08, 1)
GRAY = (0.30, 0.35, 0.39, 1)
GREEN = (0.16, 0.40, 0.25, 1)
CARD = (0.92, 0.95, 0.93, 1)
INK = (0.13, 0.19, 0.20, 1)


class BonecaApp(ShowBase):
    """Aplicação touch-first; as respostas existem apenas nesta sessão local."""

    def __init__(self):
        loadPrcFileData("boneca-digital", "window-title Minha Amiga - Boneca Digital")
        loadPrcFileData("boneca-digital", "win-size 720 1280")
        loadPrcFileData("boneca-digital", "audio-library-name p3openal_audio")
        super().__init__()
        self.enableSoundEffects(False)

        self.setBackgroundColor(247 / 255, 244 / 255, 237 / 255, 1)
        self.disableMouse()
        self.widgets = []
        self.current_screen = "home"
        self.option_actions = []
        self.discomfort_buttons = {}
        self.status_buttons = {}
        self.mood_buttons = {}
        self.intensity_buttons = {}
        self.body_hotspots = {}
        self.help_return_screen = "home"
        self.calm_return_screen = "home"
        self.sound_enabled = False
        self.audio_available = False
        self.audio_checked = False
        self.feedback_sound = None
        self.sound_toggle_button = None
        self.reaction_badge = None
        self.calm_bubble = None
        self._active_intervals = {}

        self.selected_mood = None
        self.selected_discomforts = set()
        self.discomfort_status = None
        self.selected_intensity = None
        self.selected_regions = set()

        if not MODEL_PATH.is_file():
            raise FileNotFoundError(f"Modelo 3D não encontrado: {MODEL_PATH}")
        # Registra o importador GLB fornecido por panda3d-gltf.
        import gltf  # noqa: F401

        self.character = Actor(str(MODEL_PATH))
        self.character.reparentTo(self.render)
        self._fit_character()
        self._add_lighting()
        self._setup_camera()
        self._start_idle_animation()
        self._setup_body_picker()

        # No Android o toque simples é encaminhado como mouse1 pelo Panda3D.
        self.accept("mouse1", self._on_body_touch)
        self.accept("escape", self.userExit)
        for number in range(1, 9):
            self.accept(str(number), self._run_option, [number - 1])
        self.accept("enter", self._continue_current)
        self.accept("return", self._continue_current)
        self._last_window_size = (self.win.getXSize(), self.win.getYSize()) if self.win else None
        self.accept("window-event", self._on_window_event)
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

    def _layout_aspect(self):
        """Proporção mínima segura para posicionar UI também em telas retrato."""
        return max(0.35, self.getAspectRatio() or 0.5625)

    def _choice_card_scale(self):
        return min(0.14, max(0.075, self._layout_aspect() * 0.22))

    def _title_scale(self):
        return min(0.058, max(0.046, self._layout_aspect() * 0.10))

    def _choice_side_x(self, side):
        half_width = 1.08 * self._choice_card_scale()
        x = min(0.70, self._layout_aspect() - half_width - 0.045)
        return side * max(0.18, x)

    def _corner_x(self):
        return max(0.24, self._layout_aspect() - 0.10)

    def _on_window_event(self, window):
        if window is None:
            return
        size = (window.getXSize(), window.getYSize())
        if min(size) <= 0 or size == self._last_window_size:
            return
        self._last_window_size = size
        if getattr(self, "current_screen", None):
            self.show_screen(self.current_screen)

    def _start_idle_animation(self):
        self.animations = {name.lower(): name for name in self.character.getAnimNames()}
        self.idle_animation = self.animations.get("idle")
        self.wave_animation = self.animations.get("wave")
        if self.idle_animation:
            self.character.loop(self.idle_animation)

    def _prepare_audio(self):
        if self.audio_checked:
            return
        self.audio_checked = True
        try:
            self.feedback_sound = self.loader.loadSfx(str(SOUND_PATH))
            self.audio_available = bool(
                self.feedback_sound
                and any(manager.isValid() for manager in self.sfxManagerList)
            )
            if self.audio_available:
                self.feedback_sound.setVolume(0.16)
            else:
                self.feedback_sound = None
        except Exception:
            # O app continua utilizável mesmo se o dispositivo não tiver áudio.
            self.feedback_sound = None
            self.audio_available = False

    def _greet_character(self):
        if not self.wave_animation:
            return
        self.taskMgr.remove("resume-idle-after-wave")
        self.character.play(self.wave_animation)
        self.taskMgr.doMethodLater(2.0, self._resume_idle, "resume-idle-after-wave")

    def _resume_idle(self, task):
        if self.idle_animation:
            self.character.loop(self.idle_animation)
        return Task.done

    def _setup_body_picker(self):
        self.pick_queue = CollisionHandlerQueue()
        self.picker = CollisionTraverser("body-picker")
        ray_node = CollisionNode("body-pick-ray")
        ray_node.addSolid(CollisionRay())
        ray_node.setFromCollideMask(BitMask32.bit(1))
        ray_node.setIntoCollideMask(BitMask32.allOff())
        self.ray_np = self.camera.attachNewNode(ray_node)
        self.picker.addCollider(self.ray_np, self.pick_queue)

        
        regions = [
            ("cabeça", 0.00, 0.0, 1.62, 0.17),
            ("tronco", 0.00, 0.0, 1.13, 0.27),
            ("braço direito", -0.34, 0.0, 1.12, 0.17),
            ("braço esquerdo", 0.34, 0.0, 1.12, 0.17),
            ("perna direita", -0.13, 0.0, 0.48, 0.16),
            ("perna esquerda", 0.13, 0.0, 0.48, 0.16),
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
        for interval in self._active_intervals.values():
            interval.pause()
        self._active_intervals.clear()
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()
        self.body_hotspots = {}
        self.feedback_icon = None
        self.reaction_badge = None
        self.calm_bubble = None
        self.sound_toggle_button = None

    def _label(self, text, y, scale=0.075, color=(0.13, 0.19, 0.20, 1), wordwrap=19):
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

    def _button(self, text, y, command, color=TEAL, x=0, compact=False):
        aspect = max(0.45, self.getAspectRatio())
        half_width = 3.7 if compact else 4.0
        button = DirectButton(
            parent=self.aspect2d,
            text=text,
            text_align=TextNode.ACenter,
            text_scale=0.72,
            text_fg=(1, 1, 1, 1),
            text_wordwrap=20,
            frameSize=(-half_width, half_width, -0.98, 0.98),
            frameColor=(color, color, (color[0] * 0.82, color[1] * 0.82, color[2] * 0.82, 1), color),
            relief=1,
            borderWidth=(0.025, 0.025),
            scale=min(0.24, aspect * (0.115 if compact else 0.16)),
            pos=(x, 0, y),
            command=command,
        )
        self.widgets.append(button)
        return button

    def _icon_card(self, label, icon, x, y, command, color=CARD, selected=False):
        """Cartão de escolha: pictograma grande e rótulo curto de apoio."""
        background = TEAL if selected else color
        darker = (background[0] * 0.82, background[1] * 0.82, background[2] * 0.82, 1)
        button = DirectButton(
            parent=self.aspect2d,
            text=f"X  {label}" if selected else label,
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1) if selected else INK,
            text_scale=0.30,
            text_pos=(0, -0.70),
            text_wordwrap=10,
            image=str(UI_ASSETS / f"{icon}.png"),
            image_scale=0.68,
            image_pos=(0, 0, 0.28),
            frameSize=(-1.08, 1.08, -1.08, 1.12),
            frameColor=(background, background, darker, background),
            relief=1,
            borderWidth=(0.025, 0.025),
            scale=self._choice_card_scale(),
            pos=(x, 0, y),
            command=command,
        )
        self._enable_image_alpha(button)
        self.widgets.append(button)
        return button

    def _nav_button(self, label, icon, x, y, command, color):
        """Botão grande com seta-imagem e legenda curta, sem depender do texto."""
        aspect = self._layout_aspect()
        button_scale = min(0.09, max(0.07, aspect * 0.16))
        x_limit = max(0.0, aspect - 1.8 * button_scale - 0.035)
        x = max(-x_limit, min(x_limit, x))
        darker = (color[0] * 0.82, color[1] * 0.82, color[2] * 0.82, 1)
        button = DirectButton(
            parent=self.aspect2d,
            text=label,
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_scale=0.38,
            text_pos=(0.45, -0.08),
            text_wordwrap=10,
            image=str(UI_ASSETS / f"{icon}.png"),
            image_scale=0.55,
            image_pos=(-1.02, 0, 0),
            frameSize=(-1.8, 1.8, -0.72, 0.72),
            frameColor=(color, color, darker, color),
            relief=1,
            borderWidth=(0.02, 0.02),
            scale=button_scale,
            pos=(x, 0, y),
            command=command,
        )
        self._enable_image_alpha(button)
        self.widgets.append(button)
        return button

    def _progress(self, current, total=5):
        """Etapas sem palavras: os segmentos mostram posição e avanço."""
        for index in range(total):
            done = index < current
            color = TEAL if done else (0.78, 0.82, 0.81, 1)
            bar = DirectFrame(
                parent=self.aspect2d,
                frameColor=color,
                frameSize=(-0.034, 0.034, -0.009, 0.009),
                pos=((index - (total - 1) / 2) * 0.09, 0, 0.96),
            )
            self.widgets.append(bar)

    def _add_help_button(self):
        button = DirectButton(
            parent=self.aspect2d,
            image=str(UI_ASSETS / "help_people.png"),
            image_scale=0.075,
            frameColor=(1, 1, 1, 0),
            relief=0,
            pos=(self._corner_x(), 0, 0.86),
            command=self._open_help,
        )
        self._enable_image_alpha(button)
        self.widgets.append(button)

    def _enable_image_alpha(self, widget):
        for name in widget.components():
            if name.startswith("image"):
                widget.component(name).setTransparency(TransparencyAttrib.MAlpha)

    def _stop_widget_interval(self, widget):
        interval = self._active_intervals.pop(id(widget), None)
        if interval:
            interval.pause()

    def _pulse_widget(self, widget, factor=1.08, duration=0.56, repeat=False):
        self._stop_widget_interval(widget)
        start = widget.getScale()
        peak = start * factor
        interval = Sequence(
            LerpScaleInterval(widget, duration / 2, peak, startScale=start),
            LerpScaleInterval(widget, duration / 2, start, startScale=peak),
            name=f"gentle-pulse-{id(widget)}",
        )
        self._active_intervals[id(widget)] = interval
        if repeat:
            interval.loop()
        else:
            interval.start()

    def _head_badge_position(self):
        camera_point = self.camera.getRelativePoint(self.render, Point3(0, 0, 1.56))
        point = Point2()
        if self.camLens.project(camera_point, point):
            return point.x * self.getAspectRatio() + 0.22, point.y + 0.18
        return 0.22, 0.70

    def _show_reaction(self, icon, play_sound=True):
        if self.reaction_badge is not None:
            old = self.reaction_badge
            self._stop_widget_interval(old)
            old.destroy()
            if old in self.widgets:
                self.widgets.remove(old)
        x, y = self._head_badge_position()
        self.reaction_badge = self._icon_label(icon, x, y, 0.065)
        self._pulse_widget(self.reaction_badge, factor=1.07, duration=0.48)
        if play_sound:
            self._play_feedback()

    def _clear_reaction(self):
        if self.reaction_badge is None:
            return
        badge = self.reaction_badge
        self._stop_widget_interval(badge)
        badge.destroy()
        if badge in self.widgets:
            self.widgets.remove(badge)
        self.reaction_badge = None

    def _play_feedback(self):
        if not self.sound_enabled or not self.feedback_sound:
            return
        try:
            self.feedback_sound.stop()
            self.feedback_sound.play()
        except Exception:
            self.audio_available = False
            self.sound_enabled = False
            self.enableSoundEffects(False)

    def _add_sound_toggle(self):
        x = -self._corner_x()
        icon = "sound_on" if self.sound_enabled else "sound_off"
        button = DirectButton(
            parent=self.aspect2d,
            image=str(UI_ASSETS / f"{icon}.png"),
            image_scale=0.90,
            frameColor=(1, 1, 1, 0),
            relief=0,
            scale=0.075,
            pos=(x, 0, 0.86),
            command=self._toggle_sound,
        )
        self._enable_image_alpha(button)
        self.widgets.append(button)
        self.sound_toggle_button = button

    def _toggle_sound(self):
        if not self.audio_checked:
            self._prepare_audio()
        if not self.audio_available or not self.feedback_sound:
            self.sound_enabled = False
            return
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.feedback_sound.stop()
        self.enableSoundEffects(self.sound_enabled)
        if self.sound_toggle_button:
            icon = "sound_on" if self.sound_enabled else "sound_off"
            self.sound_toggle_button["image"] = str(UI_ASSETS / f"{icon}.png")
            self._enable_image_alpha(self.sound_toggle_button)

    def _add_calm_button(self):
        x = -self._corner_x()
        button = DirectButton(
            parent=self.aspect2d,
            image=str(UI_ASSETS / "calm_bubble.png"),
            image_scale=0.90,
            frameColor=(1, 1, 1, 0),
            relief=0,
            scale=0.075,
            pos=(x, 0, 0.69),
            command=self._open_calm,
        )
        self._enable_image_alpha(button)
        self.widgets.append(button)

    def _open_calm(self):
        self.calm_return_screen = self.current_screen
        self.show_screen("calm")

    def _tap_calm_bubble(self):
        if not self.calm_bubble:
            return
        interval = self._active_intervals.get(id(self.calm_bubble))
        if interval and interval.isPlaying():
            return
        # Um único ciclo lento de crescer/encolher; toque novamente quando quiser.
        self._pulse_widget(self.calm_bubble, factor=1.16, duration=2.8)

    def _open_help(self):
        self.help_return_screen = self.current_screen
        self.show_screen("help")

    def _icon_label(self, icon, x, y, scale=0.075):
        label = DirectLabel(
            parent=self.aspect2d,
            image=str(UI_ASSETS / f"{icon}.png"),
            image_scale=scale,
            frameColor=(1, 1, 1, 0),
            pos=(x, 0, y),
        )
        self._enable_image_alpha(label)
        self.widgets.append(label)
        return label

    def _create_body_hotspots(self, selected_only=False):
        self.body_hotspots = {}
        for path in self.hit_regions:
            region = path.node().getName().split(":", 1)[1]
            selected = region in self.selected_regions
            if selected_only and not selected:
                continue
            camera_point = self.camera.getRelativePoint(self.render, path.getPos(self.render))
            point = Point2()
            if not self.camLens.project(camera_point, point):
                continue
            icon = "touch_selected" if selected else "touch_target"
            hotspot = DirectLabel(
                parent=self.aspect2d,
                image=str(UI_ASSETS / f"{icon}.png"),
                image_scale=0.08,
                frameColor=(1, 1, 1, 0),
                pos=(point.x * self.getAspectRatio(), 0, point.y),
            )
            self._enable_image_alpha(hotspot)
            self.widgets.append(hotspot)
            self.body_hotspots[region] = hotspot

    def _show_hint(self):
        self._clear_hint()
        self.feedback_icon = self._icon_label("touch_target", 0, -0.76, 0.045)

    def _clear_hint(self):
        hint = getattr(self, "feedback_icon", None)
        if hint is not None:
            hint.destroy()
            if hint in self.widgets:
                self.widgets.remove(hint)
        self.feedback_icon = None

    def _new_session(self):
        self._clear_session_data()
        self.show_screen("mood")
        self._greet_character()

    def _clear_session_data(self):
        self.selected_mood = None
        self.selected_discomforts.clear()
        self.discomfort_status = None
        self.selected_intensity = None
        self.selected_regions.clear()

    def _end_session(self):
        self._clear_session_data()
        self.show_screen("home")

    def _step(self, number, label):
        self._progress(number)

    def show_screen(self, name):
        self.clear_widgets()
        self.body_hotspots = {}
        self.current_screen = name
        self.option_actions = []
        self.mood_buttons = {}
        self.discomfort_buttons = {}
        self.status_buttons = {}
        self.intensity_buttons = {}
        self.region_label = None
        self.character.show()

        if name == "home":
            self._label("MINHA AMIGA", 0.84, 0.08, TEAL)
            self._nav_button("COMEÇAR", "nav_start", 0, -0.70, self._new_session, TEAL)

        elif name == "mood":
            self._step(1, "SENTIMENTOS")
            self._label("COMO ESTÁ?", 0.84, self._title_scale(), TEAL)
            # Carinhas em ASCII funcionam também com a fonte padrão do Panda3D.
            choices = [
                ("FELIZ", "mood_happy", GOLD, self._choice_side_x(-1.5), 0.34),
                ("BEM", "mood_ok", MINT, self._choice_side_x(1.5), 0.34),
                ("PREOCUPADO", "mood_worried", PURPLE, self._choice_side_x(-1.5), -0.08),
                ("TRISTE", "mood_sad", BLUE, self._choice_side_x(1.5), -0.08),
            ]
            self.mood_buttons = {}
            mood_short = {"FELIZ": "FELIZ", "BEM": "BEM", "PREOCUPADO": "PREOCUP.", "TRISTE": "TRISTE"}
            for choice, icon, color, x, y in choices:
                action = lambda c=choice: self._select_mood(c)
                self.option_actions.append(action)
                self.mood_buttons[choice] = self._icon_card(
                    mood_short[choice], icon, x, y, action, color=color, selected=choice == self.selected_mood
                )
            self._nav_button("VOLTAR", "nav_back", -0.40, -0.88, self._end_session, PURPLE)
            self._nav_button("SEGUIR", "nav_next", 0.40, -0.88, self._continue_mood, TEAL)

        elif name == "discomfort":
            self._step(2, "DESCONFORTO FÍSICO")
            self._label("O QUE SENTE?", 0.84, self._title_scale(), TEAL)
            self.discomfort_buttons = {}
            self.status_buttons = {}
            types = [
                ("Dor", "DOR", "sym_pain"),
                ("Enjoo ou náusea", "ENJOO", "sym_nausea"),
                ("Coceira", "COCEIRA", "sym_itch"),
                ("Tontura", "TONTURA", "sym_dizzy"),
                ("Cansaço ou sono", "SONO", "sym_tired"),
                ("Outro desconforto", "OUTRO", "sym_other"),
            ]
            left_x = self._choice_side_x(-1.5)
            right_x = self._choice_side_x(1.5)
            positions = [(left_x, 0.43), (right_x, 0.43), (left_x, 0.08), (right_x, 0.08), (left_x, -0.27), (right_x, -0.27)]
            short_names = {name: short for name, short, _ in types}
            self.discomfort_short_names = short_names
            for (name_text, short, icon), (x, y) in zip(types, positions):
                action = lambda item=name_text: self._toggle_discomfort(item)
                self.option_actions.append(action)
                self.discomfort_buttons[name_text] = self._icon_card(
                    short, icon, x, y, action, color=CARD, selected=name_text in self.selected_discomforts
                )
            status_choices = [
                ("Não sinto desconforto", "NENHUM", "status_none", left_x),
                ("Prefiro não responder", "PULAR", "status_skip", right_x),
            ]
            self.status_short_names = {status: short for status, short, _, _ in status_choices}
            for status, short, icon, x in status_choices:
                action = lambda value=status: self._set_discomfort_status(value)
                self.option_actions.append(action)
                self.status_buttons[status] = self._icon_card(
                    short, icon, x, -0.62, action, color=CARD, selected=status == self.discomfort_status
                )
            self._nav_button("VOLTAR", "nav_back", -0.40, -0.91, lambda: self.show_screen("mood"), PURPLE)
            self._nav_button("SEGUIR", "nav_next", 0.40, -0.91, self._continue_discomfort, TEAL)

        elif name == "intensity":
            self._step(3, "INTENSIDADE")
            self._label("QUANTO?", 0.84, self._title_scale(), TEAL)
            choices = [
                ("Leve", "LEVE", "intensity_low", GREEN, 0.39),
                ("Moderada", "MÉDIO", "intensity_medium", GOLD, -0.03),
                ("Forte", "FORTE", "intensity_high", RED, -0.45),
            ]
            self.intensity_buttons = {}
            self.intensity_short_names = {value: short for value, short, _, _, _ in choices}
            intensity_card_scale = min(0.095, max(0.075, self._layout_aspect() * 0.16))
            intensity_card_half_width = 1.08 * intensity_card_scale
            intensity_x = min(
                0.43,
                self._layout_aspect() - intensity_card_half_width - 0.045,
            )
            intensity_x = max(0.20, intensity_x)    
            for value, short, icon, color, y in choices:
                action = lambda level=value: self._select_intensity(level)
                self.option_actions.append(action)
                button = self._icon_card(
                    short, icon, intensity_x, y, action,
                    color=color, selected=value == self.selected_intensity
                )
                button.setScale(intensity_card_scale)
                self.intensity_buttons[value] = button
            self._nav_button("VOLTAR", "nav_back", -0.40, -0.91, lambda: self.show_screen("discomfort"), PURPLE)
            self._nav_button("SEGUIR", "nav_next", 0.40, -0.91, self._continue_intensity, TEAL)

        elif name == "body":
            self._step(4, "REGIÃO DO CORPO")
            self._label("TOQUE ONDE?", 0.84, self._title_scale(), TEAL)
            self._nav_button("VOLTAR", "nav_back", -0.40, -0.91, self._back_from_body, PURPLE)
            self._nav_button("REVISAR", "nav_next", 0.40, -0.91, lambda: self.show_screen("review"), TEAL)
            self.region_label = None
            self._create_body_hotspots()

        elif name == "review":
            self._step(5, "REVISÃO")
            self._label("REVISAR?", 0.84, self._title_scale(), TEAL)
            mood_icons = {"FELIZ": "mood_happy", "BEM": "mood_ok", "PREOCUPADO": "mood_worried", "TRISTE": "mood_sad"}
            if self.selected_mood in mood_icons:
                self._icon_label(mood_icons[self.selected_mood], -0.30, 0.54, 0.075)
            intensity_icons = {"Leve": "intensity_low", "Moderada": "intensity_medium", "Forte": "intensity_high"}
            if self.selected_intensity in intensity_icons:
                self._icon_label(intensity_icons[self.selected_intensity], 0.30, 0.54, 0.075)
            if self.discomfort_status:
                icon = "status_none" if self.discomfort_status == "Não sinto desconforto" else "status_skip"
                self._icon_label(icon, 0, 0.30, 0.065)
            else:
                icons = {
                    "Dor": "sym_pain", "Enjoo ou náusea": "sym_nausea", "Coceira": "sym_itch",
                    "Tontura": "sym_dizzy", "Cansaço ou sono": "sym_tired", "Outro desconforto": "sym_other",
                }
                for index, item in enumerate(sorted(self.selected_discomforts)):
                    row, column = divmod(index, 3)
                    self._icon_label(icons[item], (column - 1) * 0.16, 0.34 - row * 0.14, 0.045)
            self._create_body_hotspots(selected_only=True)
            self._nav_button("VOLTAR", "nav_back", -0.40, -0.91, self._back_from_review, PURPLE)
            self._nav_button("CONFIRMAR", "nav_confirm", 0.40, -0.91, self._confirm_responses, GREEN)

        elif name == "end":
            done_icon = self._icon_label("done", 0, 0.52, 0.13)
            self._pulse_widget(done_icon, factor=1.10, duration=0.72)
            self._label("PRONTO!", 0.84, self._title_scale(), TEAL)
            self._nav_button("INÍCIO", "nav_start", 0, -0.88, self._end_session, TEAL)

        elif name == "help":
            self._label("AJUDA", 0.84, self._title_scale(), BLUE)
            self._icon_label("help_people", 0, 0.34, 0.19)
            self._label("CHAME UM ADULTO", -0.03, 0.055, TEAL)
            self._nav_button("PAUSA", "calm_bubble", 0, -0.48, self._open_calm, BLUE)
            self._nav_button("VOLTAR", "nav_back", 0, -0.87, lambda: self.show_screen(self.help_return_screen), PURPLE)

        elif name == "calm":
            self._label("PAUSA", 0.84, self._title_scale(), TEAL)
            self._label("TOQUE NA BOLHA", 0.67, 0.043)
            bubble = DirectButton(
                parent=self.aspect2d,
                image=str(UI_ASSETS / "calm_bubble.png"),
                image_scale=0.78,
                frameColor=(1, 1, 1, 0),
                relief=0,
                scale=0.22,
                pos=(0, 0, 0.12),
                command=self._tap_calm_bubble,
            )
            self._enable_image_alpha(bubble)
            self.widgets.append(bubble)
            self.calm_bubble = bubble
            self._nav_button(
                "VOLTAR", "nav_back", 0, -0.88,
                lambda: self.show_screen(self.calm_return_screen), PURPLE
            )

        child_screens = {"home", "mood", "discomfort", "intensity", "body", "review", "end", "help", "calm"}
        if name in child_screens:
            self._add_sound_toggle()
        if name in {"home", "mood", "discomfort", "intensity", "body", "review", "end"}:
            self._add_calm_button()
            self._add_help_button()

    def _run_option(self, index):
        if index < len(self.option_actions):
            self.option_actions[index]()

    def _continue_current(self):
        actions = {
            "mood": self._continue_mood,
            "discomfort": self._continue_discomfort,
            "intensity": self._continue_intensity,
            "body": lambda: self.show_screen("review"),
            "review": self._confirm_responses,
            "calm": lambda: self.show_screen(self.calm_return_screen),
        }
        action = actions.get(self.current_screen)
        if action:
            action()

    def _select_mood(self, choice):
        if self.current_screen != "mood":
            return
        self.selected_mood = choice
        self._clear_hint()
        self._refresh_mood_buttons()
        icons = {"FELIZ": "mood_happy", "BEM": "mood_ok", "PREOCUPADO": "mood_worried", "TRISTE": "mood_sad"}
        self._show_reaction(icons[choice])

    def _refresh_mood_buttons(self):
        labels = {"FELIZ": "FELIZ", "BEM": "BEM", "PREOCUPADO": "PREOCUP.", "TRISTE": "TRISTE"}
        for choice, button in self.mood_buttons.items():
            selected = choice == self.selected_mood
            color = TEAL if selected else {
                "FELIZ": GOLD, "BEM": MINT,
                "PREOCUPADO": PURPLE, "TRISTE": BLUE,
            }[choice]
            darker = (color[0] * 0.82, color[1] * 0.82, color[2] * 0.82, 1)
            button["text"] = f"X  {labels[choice]}" if selected else labels[choice]
            button["text_fg"] = (1, 1, 1, 1) if selected else INK
            button["frameColor"] = (color, color, darker, color)

    def _continue_mood(self):
        if self.selected_mood is not None:
            self.show_screen("discomfort")
        else:
            self._show_hint()

    def _refresh_discomfort_options(self):
        for name, button in self.discomfort_buttons.items():
            selected = name in self.selected_discomforts
            color = TEAL if selected else CARD
            darker = (color[0] * 0.82, color[1] * 0.82, color[2] * 0.82, 1)
            short = self.discomfort_short_names[name]
            button["text"] = f"X  {short}" if selected else short
            button["text_fg"] = (1, 1, 1, 1) if selected else INK
            button["frameColor"] = (color, color, darker, color)
        for status, button in self.status_buttons.items():
            selected = status == self.discomfort_status
            color = TEAL if selected else CARD
            darker = (color[0] * 0.82, color[1] * 0.82, color[2] * 0.82, 1)
            short = self.status_short_names[status]
            button["text"] = f"X  {short}" if selected else short
            button["text_fg"] = (1, 1, 1, 1) if selected else INK
            button["frameColor"] = (color, color, darker, color)

    def _toggle_discomfort(self, name):
        if self.current_screen != "discomfort":
            return
        self._clear_hint()
        self.discomfort_status = None
        self.selected_intensity = None
        if name in self.selected_discomforts:
            self.selected_discomforts.remove(name)
        else:
            self.selected_discomforts.add(name)
        self._refresh_discomfort_options()
        icons = {
            "Dor": "sym_pain", "Enjoo ou náusea": "sym_nausea", "Coceira": "sym_itch",
            "Tontura": "sym_dizzy", "Cansaço ou sono": "sym_tired", "Outro desconforto": "sym_other",
        }
        if name in self.selected_discomforts:
            self._show_reaction(icons[name])
        elif self.selected_discomforts:
            self._show_reaction(icons[sorted(self.selected_discomforts)[-1]], play_sound=False)
        else:
            self._clear_reaction()

    def _set_discomfort_status(self, status):
        if self.current_screen != "discomfort":
            return
        self._clear_hint()
        self.selected_discomforts.clear()
        self.discomfort_status = status
        self.selected_intensity = None
        self._refresh_discomfort_options()
        self._show_reaction("status_none" if status == "Não sinto desconforto" else "status_skip")

    def _continue_discomfort(self):
        if self.discomfort_status:
            self.selected_intensity = None
            self.selected_regions.clear()
            self.show_screen("review")
        elif self.selected_discomforts:
            self.show_screen("intensity")
        else:
            self._show_hint()

    def _select_intensity(self, level):
        if self.current_screen != "intensity":
            return
        self.selected_intensity = level
        self._clear_hint()
        self._refresh_intensity_buttons()
        icons = {"Leve": "intensity_low", "Moderada": "intensity_medium", "Forte": "intensity_high"}
        self._show_reaction(icons[level])

    def _refresh_intensity_buttons(self):
        colors = {"Leve": GREEN, "Moderada": GOLD, "Forte": RED}
        for level, button in self.intensity_buttons.items():
            selected = level == self.selected_intensity
            color = TEAL if selected else colors[level]
            darker = (color[0] * 0.82, color[1] * 0.82, color[2] * 0.82, 1)
            short = self.intensity_short_names[level]
            button["text"] = f"X  {short}" if selected else short
            button["text_fg"] = (1, 1, 1, 1) if selected else INK
            button["frameColor"] = (color, color, darker, color)

    def _continue_intensity(self):
        if self.selected_intensity is not None:
            self.show_screen("body")
        else:
            self._show_hint()

    def _back_from_body(self):
        if self.discomfort_status:
            self.show_screen("discomfort")
        elif self.selected_discomforts:
            self.show_screen("intensity")
        else:
            self.show_screen("discomfort")

    def _back_from_review(self):
        if self.discomfort_status:
            self.show_screen("discomfort")
        else:
            self.show_screen("body")

    def _refresh_body_hotspots(self):
        for hotspot in self.body_hotspots.values():
            self._stop_widget_interval(hotspot)
            hotspot.destroy()
            if hotspot in self.widgets:
                self.widgets.remove(hotspot)
        self.body_hotspots = {}
        self._create_body_hotspots()

    def _pick_region(self, mouse_x, mouse_y):
        ray = self.ray_np.node().modifySolid(0)
        ray.setFromLens(self.camNode, mouse_x, mouse_y)
        self.pick_queue.clearEntries()
        self.picker.traverse(self.render)
        self.pick_queue.sortEntries()
        for index in range(self.pick_queue.getNumEntries()):
            node = self.pick_queue.getEntry(index).getIntoNodePath().node()
            if node.getName().startswith("region:"):
                return node.getName().split(":", 1)[1]
        return None

    def _on_body_touch(self):
        if self.current_screen != "body" or not self.mouseWatcherNode.hasMouse():
            return
        mouse = self.mouseWatcherNode.getMouse()
        # Ignora os controles e os rótulos; as seis zonas corporais ficam dentro desta área.
        if mouse.y < -0.86 or mouse.y > 0.82:
            return
        region = self._pick_region(mouse.x, mouse.y)
        if region:
            self._toggle_region(region)

    def _toggle_region(self, region):
        if self.current_screen != "body":
            return
        if region in self.selected_regions:
            self.selected_regions.remove(region)
        else:
            self.selected_regions.add(region)
        if self.current_screen == "body":
            self._refresh_body_hotspots()
            selected_hotspot = self.body_hotspots.get(region)
            if selected_hotspot and region in self.selected_regions:
                self._pulse_widget(selected_hotspot, factor=1.14, duration=0.64)
                self._play_feedback()

    def _confirm_responses(self):
        if self.current_screen != "review":
            return
        if self.selected_mood is None:
            return
        if not self.discomfort_status and not self.selected_discomforts:
            return
        if self.selected_discomforts and self.selected_intensity is None:
            return
        self._play_feedback()
        self.show_screen("end")
