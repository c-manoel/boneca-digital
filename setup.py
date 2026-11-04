"""Configuração do empacotamento Panda3D para Android.

Build em Linux/macOS com Panda3D 1.11+: python setup.py bdist_apps
"""
from setuptools import setup

ANDROID_PRC = """
load-display pandagles2
aux-display pandagles
window-type onscreen
"""

setup(
    name="boneca-digital",
    version="0.1.0",
    description="Protótipo offline da Boneca Digital Interativa",
    packages=["core"],
    install_requires=["panda3d-gltf>=1.2.1,<2"],
    options={
        "build_apps": {
            "platforms": ["android"],
            "gui_apps": {
                "boneca-digital": "main.py",
            },
            "application_id": "br.edu.bonecadigital",
            "android_version_code": 1,
            "android_abis": ["arm64-v8a"],
            "android_min_sdk_version": 21,
            "android_target_sdk_version": 36,
            "plugins": [
                "pandagles2",
                "pandagles",
            ],
            "include_patterns": [
                "assets/boneca_3d/*.glb",
            ],
            "extra_prc_data": ANDROID_PRC,
        },
    },
)
