import moderngl_window as mglw
from pathlib import Path
import numpy as np
from pyrr import Matrix44
import moderngl

class Test(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    title = "My Config"
    samples = 8
    resizable = False
    resource_dir = (Path(__file__).parent / '../data').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cow_scene = self.load_scene('cow/cow.obj')
        

    def render(self, time, frametime):
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        camera = np.eye(4)
        projection = np.eye(4)
        # projection = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0, dtype='f4')
        self.cow_scene.draw(projection, camera, time)

Test.run()