import moderngl_window as mglw
from pathlib import Path
import numpy as np
from pyrr import Matrix44
import moderngl
from gdv.camera import OrbitCameraWindow, OrbitDragCameraWindow

class Test(OrbitDragCameraWindow):
    gl_version = (3, 3)
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    title = "My Config"
    samples = 8
    resizable = False
    resource_dir = (Path(__file__).parent / '../resources').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cow_scene = self.load_scene('meshes/cow/cow.obj')
        self.camera.projection.update(near=0.1, far=100.0)
        self.camera.mouse_sensitivity = 0.75
        self.camera.zoom = 2.5

    def render(self, time, frametime):
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        cow_world_matrix = Matrix44.from_translation([time/10.0, 0, 0], "f4")
        self.cow_scene.draw(
            projection_matrix=self.camera.projection.matrix,
            camera_matrix=self.camera.matrix @ Matrix44.from_translation([0.5, 0, 0, 0], "f4"),
            time=time,
        )

        self.cow_scene.draw(
            projection_matrix=self.camera.projection.matrix,
            camera_matrix=self.camera.matrix @ Matrix44.from_translation([-0.5, 0, 0, 0], "f4"),
            time=time,
        )

Test.run()