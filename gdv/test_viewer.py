import moderngl_window as mglw
from pathlib import Path
import numpy as np
from pyrr import Matrix44
import moderngl
from gdv.camera import OrbitDragCameraWindow, KeyboardCamera, CameraWindow
# from moderngl_window.scene.camera import KeyboardCamera

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
        self.camera = KeyboardCamera(self.wnd.keys, fov=75.0, aspect_ratio=self.wnd.aspect_ratio, near=0.1, far=1000.0)
        self.camera.mouse_sensitivity = 0.15

    def render(self, time, frametime):
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        cow_world_matrix = Matrix44.from_translation([time/10.0, 0, 0], "f4")
        self.cow_scene.draw(
            projection_matrix=self.camera.projection.matrix,
            camera_matrix=self.camera.matrix * Matrix44.from_translation([0.5, 0, 0, 0], "f4"),
            time=time,
        )

        self.cow_scene.draw(
            projection_matrix=self.camera.projection.matrix,
            camera_matrix=self.camera.matrix * Matrix44.from_translation([-0.5, 0, 0, 0], "f4"),
            time=time,
        )

Test.run()