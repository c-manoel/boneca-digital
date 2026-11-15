# Boneca Digital Interativa — Panda3D

Protótipo local e offline para apoiar a comunicação entre criança e profissional. Não interpreta emoções ou sintomas, não realiza diagnóstico e não substitui profissionais de saúde.

## Experiência

**Início → sentimento → desconfortos físicos → intensidade → corpo → revisão → confirmação**

A interface infantil usa instruções curtas, pictogramas, botões grandes, setas e alvos visuais. Ela não exige leitura extensa nem conhecimento de Libras; os rótulos curtos continuam disponíveis como apoio para a criança, a família e a enfermagem. Cor não é a única pista: a seleção também recebe um `X` ou um símbolo de confirmação.

O layout ajusta escala e posição dos cartões e da navegação à proporção da janela. A boneca também muda de tamanho conforme a tela: fica maior na seleção do corpo e mais compacta nas telas com muitas opções; na intensidade, desloca-se levemente para abrir espaço aos cartões. Na revisão, os cartões ficam acima da boneca em retrato e em uma coluna lateral em paisagem. Na ajuda e na pausa, a ilustração/bolha fica na lateral e a boneca se desloca para o lado oposto. Os alvos de toque acompanham as transformações. Ao redimensionar ou girar o dispositivo, os controles são reconstruídos para permanecer dentro da área visível.

- Sentimentos: feliz, bem, preocupado ou triste. Os cartões destacam as ilustrações e mostram a opção escolhida com X, visto e um movimento suave; os rótulos são auxiliares.
- Desconfortos: dor, enjoo/náusea, coceira, tontura, cansaço/sono ou outro. A grade mantém marcas visíveis em cada sintoma escolhido e aceita vários ao mesmo tempo.
- “Não sinto desconforto” e “Não responder” aparecem em uma faixa separada, com pictogramas e cores próprios; são opções exclusivas e levam direto à revisão, sem exigir intensidade ou região corporal.
- Com desconfortos selecionados, a criança indica como sente por pictogramas de uma, duas ou três barras, com as palavras leve, moderada e forte como apoio. É autorrelato, não avaliação clínica.
- Na tela do corpo, cápsulas e esferas acompanham os ossos do GLB; os alvos visuais seguem a pose da boneca, e E/D identificam os lados anatômicos. As seis regiões atuais permanecem sem subdividir o tronco; um novo toque desmarca a região selecionada.
- A revisão separa sentimento, desconfortos e intensidade, aumenta os pictogramas e mostra vistos. Cada cartão abre sua tela para alterar aquela resposta; `CORRIGIR` permite rever as regiões corporais, e `CONFIRMAR` encerra a revisão.
- A ajuda mostra uma criança chamando um adulto, com uma legenda curta como apoio.
- A boneca acena ao iniciar, ao mudar a emoção escolhida e ao confirmar a revisão, retornando depois à animação idle. A seleção e a desmarcação recebem retorno visual; o pictograma de reação aparece ao lado da cabeça. Os movimentos de escala são breves, discretos e sem piscar.
- O GLB não contém rig de expressões ou blend shapes. Não há animação facial: a emoção escolhida é comunicada pelo pictograma e pela reação corporal disponível, sem deformar a malha do rosto.
- O ícone de bolha abre uma pausa opcional: a bolha fica parada ao entrar, e cada toque inicia um ciclo lento de crescer/encolher. Não há pontuação; a criança pode voltar a qualquer momento.
- O som é opcional e começa desligado. Quando ativado, usa apenas um toque curto e baixo ao selecionar, desmarcar ou confirmar; a pausa é silenciosa.
- As escolhas recebem pistas além da cor — pictogramas, vistos e/ou X — e cartões com áreas amplas de toque. As setas principais se adaptam à altura da janela; nas prévias 720×1280 e 1280×720, a altura estimada de seus alvos é de cerca de 62–65 px (pixels não equivalem necessariamente a dp físicos). A ergonomia ainda precisa ser avaliada em tablets com crianças e profissionais.

Os PNGs da interface estão em `assets/ui/`, e o toque de áudio em `assets/audio/soft_chime.wav`. Para substituir um pictograma, mantenha o nome do arquivo; para trocar ou acrescentar opções, ajuste os mapeamentos em `core/app.py`.

## Executar no computador

Requer Python 3.10 ou superior. Na pasta `boneca_digital`:

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

`Esc` fecha o protótipo. O teclado também pode ser usado: `1–4` escolhem sentimentos, `1–6` alternam desconfortos, `7` seleciona “Não sinto desconforto”, `8` seleciona “Prefiro não responder”, `1–3` escolhem intensidade e `Enter` avança quando há resposta válida. A seleção corporal é feita tocando/clicando na boneca.

## Preparar build Android

O `setup.py` configura `bdist_apps` do Panda3D para Android arm64. A build requer Python 3.13, uma build host recente do Panda3D 1.11, uma wheel Panda3D compatível com Android arm64, além de Java e Android SDK/NDK. Coloque a wheel `cp313` em `android-wheels/` e consulte as [instruções atuais do Panda3D para Android](https://discourse.panda3d.org/t/deployment-for-android/28226) para obter versões compatíveis.

```bash
python3.13 -m venv .venv-android
source .venv-android/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install --pre --extra-index-url https://archive.panda3d.org/ panda3d setuptools wheel
pip install "panda3d-gltf>=1.2.1,<2"
python setup.py bdist_apps --requirements-path requirements-android.txt
```

A configuração do projeto não equivale a um APK/AAB validado. A geração e o teste em aparelho dependem de wheels, SDK/NDK e ferramentas Android compatíveis. O identificador atual é `br.edu.bonecadigital`; altere-o antes de publicar se o grupo tiver outro identificador.

## Limitações e próximos testes

- Os alvos corporais acompanham ossos do GLB com cápsulas e esferas aproximadas; a precisão ainda precisa ser confirmada em aparelhos reais.
- A adaptação de layout precisa ser verificada em aparelhos Android reais, incluindo orientação retrato/paisagem, proporções extremas e áreas de toque.
- TalkBack/VoiceOver, foco de teclado e outras tecnologias assistivas nativas não foram integrados nem avaliados.
- Validar o vocabulário, os pictogramas e o fluxo com crianças, responsáveis, profissionais de enfermagem, acessibilidade e ética antes de qualquer uso real.
- Planejar privacidade e segurança antes de armazenar ou compartilhar respostas.

## Referências técnicas

- [Panda3D: compilação para Android](https://docs.panda3d.org/1.11/cpp/distribution/building-for-android)
- [Builds de desenvolvimento Panda3D](https://www.panda3d.org/download.php?platform=jammy&version=devel&sdk&branch=master)
- [Instruções de deployment Android e wheels](https://discourse.panda3d.org/t/deployment-for-android/28226)
