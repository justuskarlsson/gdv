import moderngl_window as mglw
from pathlib import Path
import numpy as np
from pyrr import Matrix44
import moderngl
from gdv.camera import KeyboardCamera
import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer
import numpy as np
np.set_printoptions(2, floatmode="fixed", suppress=True)
# from moderngl_window.scene.camera import KeyboardCamera

class Test(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    title = "My Config"
    samples = 8
    resizable = False
    resource_dir = (Path(__file__).parent / '../resources').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.imgui = ModernglWindowRenderer(self.wnd)
        self.camera = KeyboardCamera(self.wnd.keys, fov=75.0, aspect_ratio=self.wnd.aspect_ratio, near=0.1, far=1000.0)
        self.camera.mouse_sensitivity = 0.15

    def render(self, time, frametime):
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.render_gui()

    def render_gui(self):
        imgui.new_frame()
        imgui.begin("World", True)

        imgui.text(str(self.camera.matrix))
        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())
        self.camera_enabled = True

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)
        self.imgui.resize(width, height)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)
        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.timer.toggle_pause()
        self.imgui.key_event(key, action, modifiers)
    

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(dx, dy)
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


Test.run()