# Manos Verdes Full

Proyecto de prueba basado en la APK original de **Manos Verdes Integral**.

## Objetivo
- Instalar Manos Verdes Full en paralelo con Manos Verdes Integral.
- Mantener icono e interfaz originales.
- Agregar un botón pequeño de WhatsApp en cada pedido de la ruta (si tiene teléfono).
- Mantener compatibilidad de importación con las copias de seguridad originales.

## Estado
Este repositorio está preparando la reconstrucción reproducible desde la APK original. La APK es un artefacto compilado, no el proyecto fuente de Android/Capacitor; por eso, el proceso debe extraer y modificar sus recursos, cambiar el identificador del paquete en el manifiesto Android, volver a firmar y validar el APK resultante.

No considerar una compilación lista para instalar hasta comprobar:
1. El identificador de paquete difiere del original.
2. La firma APK es válida.
3. La aplicación se instala junto a la original.
4. El botón WhatsApp funciona en las paradas de ruta.
5. Se importa una copia de seguridad creada por la versión original.

La versión original debe conservarse como respaldo durante las pruebas.
