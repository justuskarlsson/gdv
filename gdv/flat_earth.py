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
import utm


os.environ["PYGLET_VSYNC"] = "0"

sentinel_path = "/data/sentinel-2"

class FlatEarth(moderngl_window.WindowConfig):
    title = "Flat earth"
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    resizable = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        satd.init_db(sentinel_path + "/index.db")
        resources.register_dir("/data/moderngl-resources/")
        resources.register_dir((Path(__file__).parent / "../resources").resolve())
        self.pos = [0, 0, 100]

        self.earth = moderngl_window.geometry.quad_2d(
            size=(360, 180),  # pos=(-50, 70)
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
        self.photo = imgs[1].get_rgb_photos(sentinel_path)[0]
        
        img = Image.fromarray(arr)
        img = img.resize((1000, 1000))
        self.photo_texture = self.ctx.texture(img.size, 3, np.array(img))

    def render(self, time: float, frame_time: float):
        self.ctx.clear()
        self.earth_texture.use(location=0)
        self.earth_prog["texture0"].value = 0
        projection_matrix = Matrix44.perspective_projection(
            75, 1.0, 1e-8, 1000, dtype="f4"
        )
        model_matrix = Matrix44.identity(dtype="f4")
        x, y, z = self.pos
        camera_matrix = Matrix44.look_at((x, y, z), (x, y, 0), (0, 1, 0), dtype="f4")

        self.earth_prog["m_proj"].write(projection_matrix)
        self.earth_prog["m_model"].write(model_matrix)
        self.earth_prog["m_camera"].write(camera_matrix)
        self.earth.render(self.earth_prog)

        self.photo_texture.use(location=0)
        self.photo_prog["texture0"].value = 0
        self.photo_prog["m_proj"].write(projection_matrix)
        xy_scale = self.photo.get_geod_size()
        scale = Matrix44.from_scale((*xy_scale, 1.0), dtype="f4")
        xy = self.photo.get_geod_center()
        trans = Matrix44.from_translation((*xy, 0), dtype="f4")
        self.photo_prog["m_model"].write(trans * scale)
        self.photo_prog["m_camera"].write(camera_matrix)
        self.photo_quad.render(self.photo_prog)

        # print(f"{1 / frame_time:.0f} FPS      \r", end="", flush=True)
        sleep(1 / 150.0)

    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        alpha = 0.1 * self.pos[2] / 100.0
        self.pos[0] -= dx * alpha
        self.pos[1] += dy * alpha

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        scale = 1.25
        self.pos[2] *= pow(scale, -y_offset)


if __name__ == "__main__":
    moderngl_window.run_window_config(FlatEarth)
