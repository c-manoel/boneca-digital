# Boneca Digital Interativa — protótipo

Protótipo visual em Python + Pygame para demonstração acadêmica. É local/offline, não tem banco de dados, login, internet, IA nem funcionalidades clínicas. As escolhas são apenas destacadas visualmente; não são interpretadas.

## Arquitetura

- `main.py`: inicialização do Pygame, loop principal e troca de telas.
- `config/settings.py`: dimensões, título e paleta.
- `core/screen.py`: classe-base de tela e fundo comum.
- `core/ui.py`: botões, painéis, texto e desenho vetorial da personagem.
- `screens/experience.py`: telas inicial, apresentação, emoções, corpo e encerramento.
- `assets/`: diretórios reservados para futuras imagens, sons e fontes. A versão atual desenha tudo com formas do Pygame, portanto não requer assets externos.
- `requirements.txt`: dependência necessária.

## Executar

Requer Python 3.10 ou superior. No terminal, dentro desta pasta:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

A janela abre em 960 × 640 pixels. Clique em **Começar** e siga as telas. `Esc` não encerra o app; feche a janela pelo botão de fechar do sistema.

## Roteiro de teste manual

1. Abrir o app e clicar em **COMEÇAR**.
2. Usar **VOLTAR** e **CONTINUAR** na apresentação.
3. Selecionar uma carinha; confirmar que ela fica contornada, sem interpretação da escolha.
4. Avançar, clicar em partes do corpo e confirmar que apenas a região tocada é realçada.
5. Encerrar e voltar ao início.
6. Fechar a janela e confirmar que o programa termina sem erro.

## Revisão pelo grupo

- Avaliar legibilidade, contraste, linguagem e adequação etária com profissionais e participantes apropriados antes de qualquer uso real.
- Verificar necessidades de acessibilidade, incluindo contraste, áreas clicáveis, alternativas visuais e uso em telas táteis.
- O corpo é uma representação esquemática para interação de interface, não uma ilustração anatômica nem instrumento de avaliação.
- O protótipo não substitui profissionais de saúde e não deve ser usado para decisão clínica.
- Ajustar nomes/arte e textos às orientações do projeto e às avaliações éticas/institucionais aplicáveis.
