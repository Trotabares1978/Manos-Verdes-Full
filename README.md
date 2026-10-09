# Manos Verdes Full

Reconstrucción de **Manos Verdes Full** a partir de la APK de Manos Verdes Integral entregada como referencia.

## Objetivo funcional
- Mantener las pantallas y funciones incluidas en la APK de referencia.
- Instalar Full en paralelo con Integral, sin desinstalar ni sobrescribir la original.
- Conservar el icono y sumar un botón pequeño, solo con el icono 💬, junto a Google Maps en cada parada de ruta que tenga teléfono.
- Usar la función WhatsApp existente en la interfaz.

## Reconstrucción desde la APK
La APK original se coloca localmente en `input/original.apk` (no se sube al repositorio). Ejecutar:

```bash
python3 scripts/build-apk-from-binary.py input/original.apk out/Manos-Verdes-Full-unsigned.apk
```

El script verifica que la plantilla de ruta y la función WhatsApp existan, añade el botón una sola vez, cambia el identificador Android para separar ambas instalaciones y actualiza la configuración de Capacitor.

Después se debe firmar el APK con una clave propia antes de instalarlo. Una firma nueva no permite actualizar la aplicación original ni compartir directamente sus datos privados; la migración de datos depende del mecanismo de exportación/importación de la aplicación.

## Validaciones y límites
- La modificación del HTML y la estructura ZIP se validan automáticamente.
- La firma criptográfica no demuestra por sí sola que Android vaya a instalar la APK: la instalación real debe probarse en un dispositivo.
- El cambio de identificador de paquete se mantiene de la misma longitud binaria para evitar reconstruir recursos Android compilados.
- La APK generada en este trabajo todavía necesita una prueba de instalación real en Android antes de declararse lista.
