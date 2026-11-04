# Android Panda3D wheel

Antes de executar `bdist_apps`, coloque aqui a wheel Panda3D compilada para Android, Python 3.13 e ABI `android_arm64`. O nome precisa corresponder à versão escolhida em `requirements-android.txt` (atualmente `panda3d==1.11.0`).

As wheels Android não são instaladas no ambiente desktop. Consulte as instruções de deployment Android do Panda3D para obter a wheel compatível com a build host/NDK escolhida. Não versione a wheel binária neste repositório; ela é grande e específica de ABI/toolchain.
