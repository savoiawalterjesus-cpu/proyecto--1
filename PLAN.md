# Plan del videojuego Match-3: Gemas

## 1. Resumen del proyecto

**Nombre provisional:** Gemas  
**Género:** rompecabezas Match-3 para un jugador  
**Tecnología inicial:** Python 3.10 o superior y `tkinter` (incluido en Python en la mayoría de instalaciones).  
**Plataforma inicial:** escritorio Windows; el diseño debe seguir siendo portable a macOS y Linux.  
**Estado:** prototipo jugable local. El motor, el tablero, la puntuación, los movimientos, las animaciones de intercambio/destrucción y el cargador opcional de PNG están implementados. El arte final, audio, progresión, guardado y empaquetado quedan para fases posteriores.

El jugador intercambia gemas contiguas para crear líneas de tres o más del mismo tipo, gana puntos y trata de llegar a una meta antes de agotar los movimientos. Cada tipo tiene un identificador estable (`gema_1`, `gema_2`, etc.): si su PNG está disponible se muestra esa imagen y, si falta o no se puede leer, se usa la figura geométrica provisional.

## 2. Visión y objetivos

- Ofrecer partidas cortas, comprensibles en segundos y satisfactorias al encadenar combinaciones.
- Hacer que las reglas sean deterministas y comprobables sin abrir la interfaz.
- Mantener separados el modelo del juego, la interfaz y los recursos gráficos.
- Permitir cambiar cantidad de gemas, tamaño del tablero, meta y movimientos desde configuración, sin reescribir las reglas.
- Preparar una primera versión distribuible como aplicación de escritorio.

### Criterios iniciales de éxito

- Una persona nueva puede completar su primera jugada sin instrucciones externas.
- El tablero no comienza con combinaciones automáticas y siempre dispone de al menos una jugada válida.
- Un intercambio sin combinación se revierte y no gasta un movimiento.
- Las combinaciones, cascadas, puntuación y fin de partida se comportan de forma verificable mediante pruebas.
- Las imágenes finales pueden reemplazarse conservando los identificadores de gema.

## 3. Alcance por versiones

### Prototipo actual (MVP técnico)

- Tablero de 8 x 8 y seis tipos de gema.
- Selección con ratón e intercambio de gemas adyacentes.
- Eliminación de grupos horizontales o verticales de 3 o más.
- Gravedad, reposición aleatoria y resolución de cascadas.
- 25 movimientos, objetivo de 500 puntos y botones de nueva partida.
- Rechazo de jugadas inválidas y remezcla automática si el tablero queda sin jugadas.
- Carga opcional de PNG desde `assets/gems/`; las gemas sin imagen siguen usando el dibujo provisional de `tkinter`.

### Versión 1.0 (experiencia completa)

- Crear e incorporar ilustraciones finales para `gema_1` a `gema_6`.
- Animaciones de intercambio, caída y eliminación; efectos de sonido con control de volumen.
- Pantalla de inicio, selección de nivel, pausa, victoria y derrota.
- Objetivos configurables por nivel, récord local y guardado de progreso.
- Efectos especiales por combinaciones de 4 o 5, una vez probados y equilibrados.
- Opciones de accesibilidad, pruebas de aceptación y empaquetado instalable.

### Fuera de alcance inicial

Multijugador en línea, compras, anuncios, cuentas de usuario, servicios remotos, editor de niveles y publicación móvil. Cada uno aumenta el coste de diseño, pruebas, seguridad y mantenimiento; se reconsiderarán tras validar el juego base.

## 4. Diseño de juego

### Tablero y piezas

- Rejilla cuadrada de 8 filas por 8 columnas.
- Seis familias de gemas: `gema_1`, `gema_2`, `gema_3`, `gema_4`, `gema_5`, `gema_6`.
- Cada casilla contiene exactamente un tipo de gema, salvo durante una resolución interna.
- Generar un tablero inicial sin tríos y verificar que exista al menos un movimiento válido.
- Si una resolución deja el tablero sin movimientos posibles, remezclarlo sin consumir turnos.

### Acción principal

1. El jugador selecciona una gema con el ratón.
2. Selecciona una gema ortogonalmente adyacente (arriba, abajo, izquierda o derecha).
3. El motor intercambia temporalmente las dos piezas y busca coincidencias.
4. Si no se forma ninguna línea, restaura el tablero y conserva los movimientos.
5. Si se forma una línea de 3 o más, consume un movimiento y resuelve las coincidencias.

Las diagonales no cuentan para intercambio ni para formar líneas. La selección repetida de la misma gema cancela la selección; seleccionar una pieza no vecina cambia el foco a esa pieza.

### Resolución, cascadas y puntuación

- Detectar secuencias contiguas horizontales y verticales de longitud mínima 3.
- Eliminar la unión de casillas coincidentes; una intersección horizontal/vertical se puntúa una sola vez.
- Dejar caer las gemas superiores y rellenar los espacios vacíos con tipos aleatorios.
- Repetir detección y caída hasta que no queden coincidencias.
- Puntuación base propuesta: 10 puntos por gema eliminada; multiplicador de cascada igual al número de la cadena (1x, 2x, 3x...).
- Las reglas exactas de piezas especiales y bonificaciones se decidirán con pruebas de juego, no antes de tener una curva base medible.

### Fin de partida

- Victoria al alcanzar 500 puntos.
- Derrota al llegar a cero movimientos sin alcanzar la meta.
- Tras un resultado final, bloquear las jugadas y permitir iniciar una nueva partida.
- Parámetros actuales centralizados en `main.py`; en la siguiente iteración se moverán a una configuración común para no duplicarlos.

## 5. Interfaz y experiencia

- Ventana compacta, con tablero como foco principal.
- Marcadores siempre visibles: puntuación, movimientos y objetivo.
- La selección se distingue por borde, además del color de la pieza.
- Mensajes breves para selección, intercambio inválido, objetivo logrado y fin de partida.
- Acción inequívoca de nueva partida.
- No depender solo del color para estados importantes: usar selección, texto y, más adelante, formas o símbolos diferenciados.
- En la versión animada, respetar el orden de interacción: bloquear entradas mientras se resuelven animaciones y devolver el control al completar la cascada.

## 6. Identidad de gemas y recursos

Los identificadores son datos del juego y no deben codificarse según el color, el nombre artístico ni la ruta de una imagen. Propuesta de recursos:

```text
assets/
  gems/
    gema_1.png
    gema_2.png
    gema_3.png
    gema_4.png
    gema_5.png
    gema_6.png
  audio/
  fonts/
```

El cargador busca estos nombres exactos en `assets/gems/`:

```text
assets/gems/gema_1.png
assets/gems/gema_2.png
assets/gems/gema_3.png
assets/gems/gema_4.png
assets/gems/gema_5.png
assets/gems/gema_6.png
```

El cargador PNG ya está implementado en `main.py`, usa `tkinter` sin dependencias externas y reduce las imágenes grandes para que quepan en la casilla. Requisitos recomendados para las imágenes:

- PNG con transparencia, formato cuadrado y margen interno consistente; 64 x 64 px es un buen tamaño de origen.
- Una misma escala, iluminación, perspectiva y nivel de detalle para toda la familia.
- Lectura clara al tamaño real de una casilla y siluetas distinguibles en escala de grises.
- Conservar los nombres `gema_1.png`...`gema_6.png`; cada archivo reemplaza solo su gema correspondiente.
- Guardar fuente editable, exportaciones finales y licencia/procedencia de cada recurso.
- Mantener el renderer provisional: si falta una imagen o no se puede abrir, el juego muestra automáticamente la figura geométrica.

## 7. Arquitectura Python

### Archivos actuales

- `game_core.py`: reglas puras del tablero; generación, búsqueda de coincidencias, validación de intercambio, gravedad, cascadas y remezcla.
- `main.py`: ventana `tkinter`, carga opcional de PNG, renderizado, entrada de ratón y actualización de marcadores.
- `test_game_core.py`: pruebas automatizadas de las reglas.
- `PLAN.md`: planificación, decisiones y estado del proyecto.

### Límites recomendados al crecer

- `GameConfig`: tamaño, catálogo de gemas, puntuación, movimientos y reglas por nivel.
- `Board`/`GameEngine`: estado y operaciones de juego sin dependencias de interfaz.
- `AssetManager` y renderer: extraer la carga de `main.py` aquí si crece el catálogo de recursos; ahora la carga/escala y el fallback viven en `Match3App`.
- `Match3App`: presentación e interacción; no duplicar lógica de coincidencias.
- Persistencia: módulo independiente para récord y progreso, con escritura segura y versión de esquema.
- Pruebas: motor con `unittest`; pruebas de interfaz manuales o automatizadas según la tecnología elegida.

No introducir arquitectura de servidor ni un framework de juego antes de que exista una necesidad concreta. Si animación, rendimiento o publicación multiplataforma superan las capacidades razonables de `tkinter`, evaluar Pygame como siguiente tecnología de presentación, manteniendo el motor independiente.

## 8. Modelo de datos y estados

- Tablero: matriz `grid[fila][columna]` de identificadores de gema.
- Estado de partida: puntos, movimientos restantes, objetivo, selección y estado (`jugando`, `victoria`, `derrota`).
- Configuración de nivel: dimensiones, gemas disponibles, movimientos, objetivo, reglas de puntuación y objetivos secundarios.
- Identificadores serializables: usar cadenas estables como `gema_1`, nunca índices de color o nombres de archivos como identidad.
- Invariantes: dimensiones constantes; todas las casillas ocupadas al final de cada turno; ningún trío inicial; siempre una jugada válida al empezar y después de remezclar.

## 9. Plan de trabajo y entregables

1. **Reglas base:** modelo independiente, tablero inicial válido, intercambio, detección y pruebas. Entregado en el prototipo.
2. **Bucle jugable:** entrada, dibujo provisional, puntuación, movimientos, cascadas, victoria/derrota y reinicio. Entregado en el prototipo; requiere pruebas de aceptación visual.
3. **Afinado del juego:** medir duración y dificultad; ajustar meta, movimientos, distribución aleatoria y puntuación. Pendiente de sesiones de juego.
4. **Arte y audio:** crear seis gemas y efectos; revisar licencia, contraste, lectura a tamaños pequeños y rendimiento. Pendiente de dirección artística.
5. **Contenido:** diseñar niveles, metas variadas y piezas especiales; documentar cada nivel y validar que sea resoluble. Pendiente.
6. **Progreso y accesibilidad:** guardado local, opciones, controles, contraste y preferencias de audio. Pendiente.
7. **Calidad y publicación:** pruebas de regresión, instalador, icono, instrucciones de ejecución y verificación en sistemas objetivo. Pendiente.

Cada fase termina con criterios de aceptación reproducibles, no solo con una captura de pantalla.

## 10. Pruebas y control de calidad

### Pruebas automatizadas del motor

- Tablero inicial válido, sin tríos y con al menos una jugada.
- Tríos horizontales y verticales; secuencias de 4 o más; cruces sin doble conteo.
- Intercambio adyacente válido e inválido; restauración exacta en caso inválido.
- Límite del tablero, intercambio no adyacente y tablero con cero movimientos.
- Caída y rellenado mantienen dimensiones y ocupación completa.
- Cascadas se resuelven hasta estabilidad y puntúan de manera coherente.
- Victoria, derrota y remezcla no consumen movimientos extra.
- Semilla aleatoria controlada para reproducibilidad de fallos.

### Pruebas manuales de interfaz

- Iniciar, seleccionar, cancelar selección, intercambiar vecino y seleccionar no vecino.
- Confirmar que hacer clic en huecos del tablero no elige una casilla por error.
- Comprobar mensajes, marcadores, reinicio, victoria y derrota.
- Ejecutar en distintas escalas de pantalla y verificar que toda la ventana sea visible.
- Sustituir una imagen por tipo y verificar que la lógica no cambia.

### Criterio de salida de versión

Todas las pruebas del motor pasan; no hay errores de interfaz en el flujo principal; las reglas se explican en una pantalla o ayuda breve; los recursos están licenciados; y se puede iniciar una partida desde la aplicación empaquetada.

## 11. Riesgos y decisiones abiertas

- **Aleatoriedad injusta:** registrar semillas en pruebas, asegurar jugadas disponibles y analizar distribución. No prometer que todo nivel es resoluble si el diseño aún depende del azar.
- **Interfaz demasiado básica:** `tkinter` facilita el prototipo, pero las animaciones y controles de juego sofisticados pueden justificar migrar a Pygame.
- **Piezas distinguibles solo por color:** diseñar siluetas, facetas o símbolos accesibles además del color.
- **Alcance creciente:** terminar y probar el bucle principal antes de introducir mapa, economía, poderes o servicios en línea.
- **Guardado corrupto o incompatible:** versionar datos y usar escritura atómica cuando se añada persistencia.
- **Arte sin derechos claros:** mantener inventario de autor, licencia y origen de cada recurso antes de distribuir.

Decisiones por resolver con el propietario: nombre final y tema visual; audiencia/plataforma final; si será un juego de niveles o infinito; objetivos y curva de dificultad; estilo de arte y licencias; necesidad de música, controles de teclado o publicación fuera de Windows.

## 12. Siguientes pasos recomendados

1. Ejecutar `python main.py` y probar una partida completa en el equipo objetivo.
2. Elegir una dirección visual y guardar las seis imágenes como `assets/gems/gema_1.png`...`gema_6.png`; el juego las detectará automáticamente sin cambiar las reglas.
3. Añadir pruebas de cascadas, cruces y remezcla antes de expandir el contenido.
4. Hacer una sesión breve de juego para ajustar los 500 puntos y 25 movimientos.
5. Decidir si la versión 1.0 sigue con `tkinter` o necesita migrar la presentación a Pygame.
6. Después, priorizar niveles y persistencia local; dejar multijugador y economía para una decisión de producto posterior.
