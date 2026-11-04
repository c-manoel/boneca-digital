# Boneca Digital Interativa — protótipo Panda3D

Protótipo acadêmico, local e offline, para apoiar a comunicação entre criança e profissional. O aplicativo não realiza diagnóstico, não interpreta emoções ou sintomas e não substitui profissionais de saúde.

## Arquitetura

A interface inteira é feita com Panda3D: a janela, os textos, os botões e a boneca 3D usam o mesmo motor gráfico. `core/app.py` controla as telas e a navegação; `main.py` inicia a aplicação; o modelo e suas animações estão em `assets/boneca_3d/grab3d-lowpoly-character.glb`. Os toques são recebidos pelo sistema de eventos do Panda3D. Na tela do corpo, um raio de colisão identifica uma região aproximada.

As regiões são áreas de interação aproximadas, e não uma representação anatômica ou ferramenta de avaliação. A escolha apenas destaca a região indicada pela pessoa.

## Requisitos

- Python 3.10 ou superior para testar no computador; a build Android descrita pelo Panda3D usa Python 3.13 e wheels específicas para Android.
- O build Android deve ser feito em Linux ou macOS com Java e Android SDK/NDK configurados.
- O renderer Android configurado é `pandagles2`, com `pandagles` como alternativa. O Pygame não é usado nesta versão.

## Testar no computador

Na pasta do projeto:

```bash
python3 -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install --pre --extra-index-url https://archive.panda3d.org/ -r requirements.txt
python main.py
```

A janela Panda3D abre com a tela inicial. Use mouse ou toque quando o dispositivo permitir. `Esc` fecha o protótipo.

## Telas e teste manual

O fluxo é: **Início → Apresentação → Como você está? → Corpo → Encerramento**. Teste os botões grandes, voltar/continuar, as cinco opções de humor e os cliques/toques na cabeça, tronco, braços e pernas. Na tela de corpo, a interface mostra a região aproximada escolhida. O app não infere causa nem gravidade.

O modelo contém animações; quando a animação `idle` está disponível, ela inicia automaticamente. A seleção por colisores é independente da animação e deve ser conferida visualmente no modelo real.

## Gerar pacote Android

O `setup.py` configura `bdist_apps` do Panda3D para Android arm64. O fluxo Android requer Python 3.13, uma build host recente do Panda3D 1.11 e uma wheel Panda3D compilada para o alvo Android. Coloque a wheel `cp313` para `android_arm64` na pasta `android-wheels/`. As wheels específicas e o estado de suporte podem mudar; consulte as [instruções atuais da comunidade Panda3D para Android](https://discourse.panda3d.org/t/deployment-for-android/28226) antes de baixar os arquivos. Configure também Java e Android SDK/NDK no ambiente.

```bash
python3.13 -m venv .venv-android
source .venv-android/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install --pre --extra-index-url https://archive.panda3d.org/ panda3d setuptools wheel
pip install "panda3d-gltf>=1.2.1,<2"
python setup.py bdist_apps --requirements-path requirements-android.txt
```

O comando deve gerar um Android App Bundle (`.aab`) dentro de `dist/`. Para instalar e testar em um aparelho, use as ferramentas Android (`adb`/`bundletool`) para converter ou instalar o bundle. O `application_id` atual é `br.edu.bonecadigital`; altere-o antes de publicar se o grupo tiver um identificador próprio. `android_version_code` começa em `1` e deve aumentar em cada versão publicada. O teste desktop é reproduzível com os comandos acima; a build Android continua dependendo das wheels correspondentes e do SDK/NDK.

## Observações para revisão do grupo

- Testar em aparelhos Android reais com proporções de tela diferentes, orientação retrato e áreas reservadas pelo sistema.
- Conferir tamanho e legibilidade dos textos e botões com crianças e profissionais apropriados; os elementos foram feitos grandes para toque, mas ainda precisam de avaliação.
- Ajustar as esferas de colisão de cada região ao personagem, pois são aproximações em coordenadas fixas e não acompanham os ossos durante animações.
- Confirmar licenças e permissão de uso do modelo GLB antes de distribuir o aplicativo.
- O código e a configuração Android foram preparados para teste; a geração do `.aab` e o teste em dispositivo dependem do SDK/NDK Android e de aparelho compatível.

## Referências técnicas

- [Panda3D: compilação para Android](https://docs.panda3d.org/1.11/cpp/distribution/building-for-android)
- [Builds de desenvolvimento Panda3D](https://www.panda3d.org/download.php?platform=jammy&version=devel&sdk&branch=master)
- [Instruções de deployment Android e wheels](https://discourse.panda3d.org/t/deployment-for-android/28226)
