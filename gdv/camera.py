import moderngl_window as mglw
from moderngl_window.scene.camera import OrbitCamera, Camera

class CameraWindow(mglw.WindowConfig):
    """Base class with built in 3D camera support"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)

        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def mouse_position_event(self, x: int, y: int, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(-dx, -dy)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

class OrbitDragCameraWindow(mglw.WindowConfig):
    """Base class with drag-based 3D orbit support

    Click and drag with the left mouse button to orbit the camera around the view point.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = OrbitCamera(aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)
        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def mouse_drag_event(self, x: int, y: int, dx, dy):
        self.camera.rot_state(dx, dy)

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        self.camera.zoom_state(y_offset)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)



import time

import numpy
from moderngl_window.utils.keymaps import QWERTY, KeyMapFactory
from pyrr import Vector3, Matrix44, vector, vector3
from moderngl_window.context.base import BaseKeys

# Direction Definitions
RIGHT = 1
LEFT = 2
FORWARD = 3
BACKWARD = 4
UP = 5
DOWN = 6

# Movement Definitions
STILL = 0
POSITIVE = 1
NEGATIVE = 2


class KeyboardCamera(Camera):
    """Camera controlled by mouse and keyboard.
    The class interacts with the key constants in the
    built in window types.

    Creating a keyboard camera:

    .. code:: python

        camera = KeyboardCamera(
            self.wnd.keys,
            fov=75.0,
            aspect_ratio=self.wnd.aspect_ratio,
            near=0.1,
            far=1000.0,
        )

    We can also interact with the belonging
    :py:class:`~moderngl_window.opengl.projection.Projection3D` instance.

    .. code:: python

        # Update aspect ratio
        camera.projection.update(aspect_ratio=1.0)

        # Get projection matrix in bytes (f4)
        camera.projection.tobytes()
    """

    def __init__(self, keys: BaseKeys, keymap: KeyMapFactory = QWERTY, fov=60.0, aspect_ratio=1.0, near=1.0, far=100.0):
        """Initialize the camera

        Args:
            keys (BaseKeys): The key constants for the current window type
        Keyword Args:
            keymap (KeyMapFactory) : The keymap to use. By default QWERTY.
            fov (float): Field of view
            aspect_ratio (float): Aspect ratio
            near (float): near plane
            far (float): far plane
        """
        # Position movement states
        self.keys = keys
        self.keymap = keymap(keys)
        self._xdir = STILL
        self._zdir = STILL
        self._ydir = STILL
        self._last_time = 0
        self._last_rot_time = 0

        # Velocity in axis units per second
        self._velocity = 10.0
        self._mouse_sensitivity = 0.5

        super().__init__(fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)

    @property
    def mouse_sensitivity(self) -> float:
        """float: Mouse sensitivity (rotation speed).

        This property can also be set::

            camera.mouse_sensitivity = 2.5
        """
        return self._mouse_sensitivity

    @mouse_sensitivity.setter
    def mouse_sensitivity(self, value: float):
        self._mouse_sensitivity = value

    @property
    def velocity(self):
        """float: The speed this camera move based on key inputs

        The property can also be modified::

            camera.velocity = 5.0
        """
        return self._velocity

    @velocity.setter
    def velocity(self, value: float):
        self._velocity = value

    def key_input(self, key, action, modifiers) -> None:
        """Process key inputs and move camera

        Args:
            key: The key
            action: key action release/press
            modifiers: key modifier states such as ctrl or shit
        """
        # Right
        if key == self.keymap.RIGHT:
            if action == self.keys.ACTION_PRESS:
                self.move_right(True)
            elif action == self.keys.ACTION_RELEASE:
                self.move_right(False)
        # Left
        elif key == self.keymap.LEFT:
            if action == self.keys.ACTION_PRESS:
                self.move_left(True)
            elif action == self.keys.ACTION_RELEASE:
                self.move_left(False)
        # Forward
        elif key == self.keymap.FORWARD:
            if action == self.keys.ACTION_PRESS:
                self.move_forward(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_forward(False)
        # Backwards
        elif key == self.keymap.BACKWARD:
            if action == self.keys.ACTION_PRESS:
                self.move_backward(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_backward(False)

        # DOWN
        elif key == self.keymap.DOWN:
            if action == self.keys.ACTION_PRESS:
                self.move_down(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_down(False)

        # UP
        elif key == self.keymap.UP:
            if action == self.keys.ACTION_PRESS:
                self.move_up(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_up(False)

    def move_left(self, activate) -> None:
        """The camera should be continiously moving to the left.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(LEFT, activate)

    def move_right(self, activate) -> None:
        """The camera should be continiously moving to the right.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(RIGHT, activate)

    def move_forward(self, activate) -> None:
        """The camera should be continiously moving forward.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(FORWARD, activate)

    def move_backward(self, activate) -> None:
        """The camera should be continiously moving backwards.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(BACKWARD, activate)

    def move_up(self, activate) -> None:
        """The camera should be continiously moving up.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(UP, activate)

    def move_down(self, activate):
        """The camera should be continiously moving down.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(DOWN, activate)

    def move_state(self, direction, activate) -> None:
        """Set the camera position move state.

        Args:
            direction: What direction to update
            activate: Start or stop moving in the direction
        """
        if direction == RIGHT:
            self._xdir = POSITIVE if activate else STILL
        elif direction == LEFT:
            self._xdir = NEGATIVE if activate else STILL
        elif direction == FORWARD:
            self._zdir = NEGATIVE if activate else STILL
        elif direction == BACKWARD:
            self._zdir = POSITIVE if activate else STILL
        elif direction == UP:
            self._ydir = POSITIVE if activate else STILL
        elif direction == DOWN:
            self._ydir = NEGATIVE if activate else STILL

    def rot_state(self, dx: int, dy: int) -> None:
        """Update the rotation of the camera.

        This is done by passing in the relative
        mouse movement change on x and y (delta x, delta y).

        In the past this method took the viewport position
        of the mouse. This does not work well when
        mouse exclusivity mode is enabled.

        Args:
            dx: Relative mouse position change on x
            dy: Relative mouse position change on y
        """
        dx, dy = -dx, -dy
        now = time.time()
        delta = now - self._last_rot_time
        self._last_rot_time = now

        # Greatly decrease the chance of camera popping.
        # This can happen when the mouse enters and leaves the window
        # or when getting focus again.
        if delta > 0.1 and max(abs(dx), abs(dy)) > 2:
            return

        dx *= self._mouse_sensitivity
        dy *= self._mouse_sensitivity

        self._yaw -= dx
        self._pitch += dy

        if self.pitch > 85.0:
            self.pitch = 85.0
        if self.pitch < -85.0:
            self.pitch = -85.0

        self._update_yaw_and_pitch()

    @property
    def matrix(self) -> numpy.ndarray:
        """numpy.ndarray: The current view matrix for the camera"""
        # Use separate time in camera so we can move it when the demo is paused
        now = time.time()
        # If the camera has been inactive for a while, a large time delta
        # can suddenly move the camera far away from the scene
        t = max(now - self._last_time, 0)
        self._last_time = now
        global_movement = False
        if global_movement:
            x_dir = Vector3([1, 0, 0])
            y_dir = Vector3([0, -1, 0])
            z_dir = Vector3([0, 0, -1])
        else:
            x_dir = self.right
            # Temp fix, q is mapped to UP
            y_dir = -self.up
            z_dir = self.dir
        # X Movement
        if self._xdir == POSITIVE:
            self.position += x_dir * self._velocity * t
        elif self._xdir == NEGATIVE:
            self.position -= x_dir * self._velocity * t

        # Z Movement
        if self._zdir == NEGATIVE:
            self.position += z_dir * self._velocity * t
        elif self._zdir == POSITIVE:
            self.position -= z_dir * self._velocity * t

        # Y Movement
        if self._ydir == POSITIVE:
            self.position += y_dir * self._velocity * t
        elif self._ydir == NEGATIVE:
            self.position -= y_dir * self._velocity * t

        return self._gl_look_at(self.position, self.position + self.dir, self._up)
