from pyrr import Matrix44
import moderngl
from pathlib import Path
import moderngl_window
from moderngl_window import resources
import os
from time import sleep

os.environ["PYGLET_VSYNC"] = "0"

class FlatEarth(moderngl_window.WindowConfig):
    title="Flat earth"
    window_size = (1920, 1080)
    aspect_ratio = 16/9
    resizable=False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        resources.register_dir("/data/moderngl-resources/")
        resources.register_dir((Path(__file__).parent / '../resources').resolve())
        
        self.quad = moderngl_window.geometry.quad_2d(
            size=(360, 180), #pos=(-50, 70)
        )
        self.texture = self.load_texture_2d('textures/land_shallow_topo_2048.jpg')
        self.prog = self.load_program('programs/cube_simple_texture.glsl')
        # self.prog = self.load_program('programs/texture.glsl')
        self.pos = [0, 0, 100]

    def render(self, time: float, frame_time: float):
        self.ctx.clear()
        self.texture.use(location=0)
        self.prog['texture0'].value = 0
        projection_matrix = Matrix44.perspective_projection(75, 1.0, 1, 1000, dtype='f4')
        # projection_matrix = Matrix44.identity(dtype="f4")
        # projection_matrix = Matrix44.orthogonal_projection(
        #     -500, 500,
        #     -500, 500,
        #     0.0, 1000.0,
        #     dtype='f4',
        # )
        # print(f"{1 / frame_time:.0f} FPS      \r", end="", flush=True)
        model_matrix = Matrix44.identity(dtype="f4") 
        x, y, z = self.pos
        camera_matrix = Matrix44.look_at((x, y, z), (x, y, 0), (0, 1, 0), dtype="f4")
        self.prog['m_proj'].write(projection_matrix)
        self.prog['m_model'].write(model_matrix)
        self.prog['m_camera'].write(camera_matrix)
        self.quad.render(self.prog)

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
