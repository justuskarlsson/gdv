from OpenGL.GL import *
from OpenGL.GLU import *

class Shader:
    def __init__(self, vertexShader: str, fragmentShader: str):
        ...

    def _compile_shader(self, shaderCode: str, shader_type=GL_VERTEX_SHADER):
        uid = glCreateShader(shader_type)
        glShaderSource(uid, 1, shaderCode, )