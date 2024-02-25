from pyrr import Matrix44
import moderngl
import moderngl_window


class FlatEarth(moderngl_window.WindowConfig):
    title="Flat earth"
    window_size = (1920, 1080)
    aspect_ratio = 16/9
    resizable=False
    resource_dir = "/data/moderngl-resources/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quad = moderngl_window.geometry.quad_2d(
            size=(360, 180), #pos=(-50, 70)
        )
        self.texture = self.load_texture_2d('textures/land_shallow_topo_2048.jpg')
        self.prog = self.load_program('programs/cube_simple_texture.glsl')
        # self.prog = self.load_program('programs/texture.glsl')


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
        model_matrix = Matrix44.identity(dtype="f4") 
        camera_matrix = Matrix44.look_at((time, 0, -100 - time), (0, 0, 0), (0, 1, 0), dtype="f4")
        self.prog['m_proj'].write(projection_matrix)
        self.prog['m_model'].write(model_matrix)
        self.prog['m_camera'].write(camera_matrix)
        self.quad.render(self.prog)

if __name__ == "__main__":
    moderngl_window.run_window_config(FlatEarth)
