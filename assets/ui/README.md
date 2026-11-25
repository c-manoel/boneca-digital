# Pictogramas da interface

Os arquivos são PNGs RGBA de 128 × 128 px, usados em cartões de escolha, navegação, ajuda e indicação de toque. O aplicativo habilita a transparência alfa ao carregá-los.

| Arquivo | Uso |
|---|---|
| `mood_happy.png`, `mood_ok.png`, `mood_worried.png`, `mood_sad.png` | Sentimentos |
| `sym_pain.png`, `sym_nausea.png`, `sym_itch.png`, `sym_dizzy.png`, `sym_tired.png`, `sym_other.png` | Tipos de desconforto |
| `status_none.png`, `status_skip.png` | Nenhum desconforto / prefiro não responder |
| `intensity_low.png`, `intensity_medium.png`, `intensity_high.png` | Intensidade |
| `touch_target.png`, `touch_selected.png` | Alvos e marcação das regiões corporais |
| `nav_back.png`, `nav_next.png`, `nav_confirm.png`, `nav_start.png` | Navegação |
| `help_people.png`, `done.png` | Ajuda e conclusão |
| `sound_off.png`, `sound_on.png` | Controle visual do som opcional |
| `calm_bubble.png` | Atalho e bolha da pausa tranquila |

Para trocar um desenho, mantenha o nome do arquivo e a transparência do PNG. Se criar uma opção nova, atualize também os mapeamentos de tela e seleção em `core/app.py`. Evite depender apenas de uma cor para comunicar estado; mantenha formas distintas e contraste forte.



## Atualização visual infantil
Os pictogramas foram atualizados com cores mais vivas e aparência amigável.
Os nomes originais foram preservados para permitir substituir os arquivos de assets.
Todos os PNGs mantêm transparência RGBA. Os arquivos que eram 128 x 128 continuam
128 x 128; `help_call_adult.png` permanece 256 x 256.
