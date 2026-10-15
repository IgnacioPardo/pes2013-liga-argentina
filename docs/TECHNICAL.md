# Notas técnicas

## Equipos

La conversión utiliza las estructuras del PES/WE Option File Editor. Se copian 24 clubes y 675 jugadores del guardado argentino 2012. La asignación protege los IDs usados por selecciones y clubes que no se reemplazan, y utiliza slots desplazados o de jugadores editados vacíos.

Se trasladan los nombres, escudos, formaciones, dorsales, planteles y uniformes. Los índices de escudos personalizados se ajustan por la diferencia de cinco entradas entre ambas bases. Los callnames incompatibles se desactivan para evitar apellidos incorrectos.

## Closs

El donante de audio utiliza PES 2014. Su banco tiene 9.202 entradas; las primeras 4.918 son audio. El banco español esperado por PES 2013 tiene 5.824 entradas. Copiar manteniendo los mismos números produce relatos incorrectos e incluso intenta reproducir texturas.

Los overlays `realconditionS.ovl` tienen 3.332 registros de 16 bytes entre `0x80` y `0xd0c0`: 3.326 eventos de audio y seis comandos. Las condiciones coinciden; sólo cambian los IDs de audio. El grafo posterior coincide al normalizar los punteros de reubicación.

`repack-commentary.py` construye el mapa a partir de esas condiciones. Ejemplo: evento 5169 de PES 2013 → audio 4374 del donante. Las 2.498 posiciones no referenciadas usan un clip comprobado como silencio. Tres entradas ADX se convierten a ATRAC3. El resultado mantiene el inventario de 5.824 archivos RIFF.

El banco `SSOUND.cpk` se agrega al directorio de la ISO USA. La preferencia de relato usa idioma 4 y la de texto usa idioma 11.

## Hinchadas

Se reemplazan 25 IDs exclusivos de los clubes sustituidos, manteniendo el inventario de 692 entradas de `0SOUND.cpk`. La tabla de cinco cánticos por equipo está en el offset `0x29a678` del EBOOT descifrado de la base comprobada.

Los clips usan ATRAC3+ estéreo con bloques de 2.048 bytes. La cabecera conserva el formato RIFF/Sony nativo de 100 bytes, los campos extendidos de `fact` y la compensación que produce un primer sample válido de 2.416. Cambiar sólo el contenedor sin conservar esos campos causaba problemas de reproducción.

## Uniformes nacionales

La ISO base proporcionada, con un guardado nuevo, mostraba Argentina amarilla/celeste y Brasil verde. Se importaron los cuatro uniformes editables de cada selección desde el archivo argentino 2012. El arreglo puntual cambió 337 bytes y conservó el resto del guardado. No se atribuye este comportamiento a todas las copias comerciales de PES 2013.

## Límites de la implementación

Los offsets y verificaciones corresponden a la base USA ULUS10597 y los donantes acreditados. Otra edición requiere investigar y validar sus tablas. Este proyecto modifica datos y recursos del juego: no cambia el núcleo PPSSPP ni añade compatibilidad multijugador con PES de PC.
