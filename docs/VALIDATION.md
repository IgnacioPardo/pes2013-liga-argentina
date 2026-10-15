# Validación registrada

Pruebas funcionales realizadas el 9 de octubre de 2026 con RetroArch/PPSSPP nativo en macOS:

- Se llegó a partidos Boca–River, Boca–San Lorenzo y Boca–Racing.
- La grabación de cánticos de Boca coincidió con un clip de origen (correlación normalizada 0,778).
- El silbato inicial y múltiples relatos durante Boca–Racing coincidieron con Closs; varias coincidencias alcanzaron 0,74–0,94.
- Se comprobaron visualmente los uniformes titular y alternativo de Argentina y Brasil.
- DualSense configurado como jugador 1.
- El usuario confirmó juego fluido al finalizar las grabaciones y los análisis. No se aisló una causa única de los tirones observados durante esas tareas.

Los resultados numéricos se resumen en [validation.json](validation.json). Las grabaciones y clips originales quedan en el entorno de trabajo local.

## Transferencia a Apple TV

Se transfirieron la ISO de 2.005.782.528 bytes, el archivo de opciones y las miniaturas/listas. Los archivos pequeños se descargaron nuevamente y se compararon mediante SHA-256. El tamaño remoto de la ISO coincidió y los primeros 1.083.365.936 bytes descargados coincidieron con el original local. La conexión de lectura terminó antes de completar la ISO; no se estableció su SHA-256 remoto completo.

No se lanzó esta versión final en el Apple TV durante esa comprobación. Las pruebas de juego descritas arriba corresponden al Mac. Tampoco se verificaron temporadas completas, todos los modos, todos los equipos ni juego online.

## Publicación del código

Preparar el repositorio no implica volver a ejecutar los partidos. Las verificaciones del empaquetado comprueban la sintaxis, las versiones fijadas de las herramientas y los archivos que entran en Git. Cualquier cambio futuro en bancos, tablas o uniformes debe probarse en el juego.
