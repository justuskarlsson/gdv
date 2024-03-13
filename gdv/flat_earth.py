from pyrr import Matrix44
import moderngl
from pathlib import Path
import moderngl_window
from moderngl_window import resources
import os
from time import sleep
import satd
from PIL import Image
import numpy as np
import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer
import random

np.set_printoptions(2, floatmode="fixed", suppress=True)

os.environ["PYGLET_VSYNC"] = "0"

sentinel_path = "/data/sentinel-2"

WIDTH = 1920
HEIGHT = 1080

class FlatEarth(moderngl_window.WindowConfig):
    title = "Flat earth"
    window_size = (WIDTH, HEIGHT)
    aspect_ratio = WIDTH / HEIGHT
    resizable = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.wnd.ctx.error
        self.imgui = ModernglWindowRenderer(self.wnd)
        satd.init_db(sentinel_path + "/index.db")
        resources.register_dir("/data/moderngl-resources/")
        resources.register_dir((Path(__file__).parent / "../resources").resolve())
        self.pos = [15.608193, 58.41614, -0.025]

        self.earth = moderngl_window.geometry.quad_2d(
            size=(360, 180),
        )
        self.earth_texture = self.load_texture_2d("textures/land_shallow_topo_2048.jpg")
        self.earth_prog = self.load_program("programs/cube_simple_texture.glsl")

        self.photo_quad = moderngl_window.geometry.quad_2d(
            size=(1.0, 1.0),  # pos=(-50, 70)
        )
        self.photo_prog = self.load_program("programs/cube_simple_texture.glsl")
        # self.prog = self.load_program('programs/texture.glsl')
        
        # # Uncomment to see sat image
        imgs = satd.SentinelImage.select()
        arr = imgs[1].get_rgb(sentinel_path)
        self.photos = imgs[1].get_rgb_photos(sentinel_path)
        self.photo = self.photos[0]
        
        img = Image.fromarray(arr)
        img = img.resize((1000, 1000))
        self.set_texture(img)
        self.photo_xy = self.photo.get_geod_center()
        self.photo_xy_sc = self.photo.get_geod_size()


    def set_texture(self, img: Image.Image):
        self.photo_texture = self.ctx.texture(img.size, 3, np.array(img))

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        # Hides texture img
        # self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        x, y, z = self.pos
        self.ctx.clear()
        self.earth_texture.use(location=0)
        self.earth_prog["texture0"].value = 0
        # projection_matrix = Matrix44.perspective_projection(
        #     75, 1.0, 1e-8, 1000, dtype="f4"
        # )
        # self.aspect_ratio
        prj_x = z * self.aspect_ratio
        prj_y = z
        projection_matrix = Matrix44.orthogonal_projection(
            -prj_x, prj_x, prj_y, -prj_y, 1, 1e8, dtype="f4"
        )
        model_matrix = Matrix44.identity(dtype="f4")
        camera_matrix = Matrix44.look_at((x, y, z), (x, y, 0), (0, 1, 0), dtype="f4")

        self.earth_prog["m_proj"].write(projection_matrix)
        self.earth_prog["m_model"].write(model_matrix)
        self.earth_prog["m_camera"].write(camera_matrix)
        self.earth.render(self.earth_prog)
        # print("https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/opengl-perspective-projection-matrix.html")
        # print(camera_matrix.T)
        # print(projection_matrix.T)
        self.photo_texture.use(location=0)
        self.photo_prog["texture0"].value = 0
        self.photo_prog["m_proj"].write(projection_matrix)
        scale = Matrix44.from_scale((*self.photo_xy_sc, 1.0), dtype="f4")
        trans = Matrix44.from_translation((*self.photo_xy, 0), dtype="f4")
        self.photo_prog["m_model"].write(trans * scale)
        self.photo_prog["m_camera"].write(camera_matrix)
        P = np.array(projection_matrix.T)
        CM = np.array(camera_matrix.T)
        C = P @ CM
        C /= C[3, 3]
        uvw = C @ np.array([15, 58, 0, 1], dtype=np.float32).T
        # uvw = projection_matrix * (camera_matrix * pyrr.Vector4([15, 58, 0, 1], dtype="f4"))
        uvw /= uvw[3]
        
        # print(self.pos)
        # print(uvw)

        
        C_inv = np.linalg.pinv(C)
        C_inv /= C_inv[3, 3]
        self.C_inv = C_inv

        self.photo_quad.render(self.photo_prog)

        # print(f"{1 / frame_time:.0f} FPS      \r", end="", flush=True)
        self.render_gui()
        sleep(1 / 150.0)

    def get_east_north(self, x_clip, y_clip):
        x = self.C_inv @ np.array([x_clip, y_clip, 0, 1], dtype=np.float32)
        x /= x[3]
        return x[:2]

    def render_gui(self):
        imgui.new_frame()
        imgui.set_next_window_size(200, HEIGHT)
        imgui.set_next_window_position(WIDTH - 200, 0)
        imgui.begin("World", False)

        if imgui.button("Update Image") or random.random() < 0.01:
            e1, n1 = self.get_east_north(-1, 1)
            e2, n2 = self.get_east_north(1, -1)
            img = satd.Photo.read_all_aoi(self.photos, e1, n1, e2, n2, WIDTH, HEIGHT)
            self.set_texture(img)
            self.photo_xy = ((e2 + e1) / 2, (n1 + n2) / 2)
            self.photo_xy_sc = (e2 - e1, n2 - n1)
        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())
        self.camera_enabled = True


    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        alpha = 0.1 * self.pos[2] / 100.0
        self.pos[0] += dx * alpha
        self.pos[1] -= dy * alpha
        self.imgui.mouse_drag_event(x, y, dx, dy)


    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        scale = 1.25
        self.pos[2] *= pow(scale, -y_offset)
        self.imgui.mouse_scroll_event(x_offset, y_offset)


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

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)

if __name__ == "__main__":
    moderngl_window.run_window_config(FlatEarth)
