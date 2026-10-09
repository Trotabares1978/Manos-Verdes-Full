# Manos Verdes Full

Reconstrucción Android independiente de **Manos Verdes Integral**, destinada a instalarse en paralelo y probarse sin borrar la aplicación original.

## Obtener la APK de prueba

La compilación automática está configurada en [GitHub Actions](https://github.com/Trotabares1978/Manos-Verdes-Full/actions), rama `clean-rebuild`.

1. Abrí la ejecución más reciente de **Build Manos Verdes Full**.
2. Esperá a que el trabajo termine en verde.
3. En **Artifacts**, descargá `Manos-Verdes-Full-debug`.
4. Descomprimí el ZIP e instalá `app-debug.apk` en Android. Si Android lo solicita, autorizá temporalmente la instalación desde esa fuente.

El paquete configurado es `ar.com.manosverdes.full`, distinto del original `com.manosverdes.integral`; la intención es que ambas aplicaciones puedan convivir. La APK de depuración no está pensada para publicarse en una tienda.

## Compilación reproducible

Requiere Node.js 22, Java 21 y Android SDK (el runner de GitHub Actions ya proporciona el entorno Android).

```bash
npm install
npm test
npm run build:web
npx cap add android
npx cap sync android
cd android
./gradlew assembleDebug --no-daemon
```

El APK se genera en `android/app/build/outputs/apk/debug/app-debug.apk`.

## Estado y alcance

- La compilación automática ejecuta primero las pruebas de humo.
- La prueba de compilación no sustituye una instalación y prueba funcional en un teléfono.
- La interfaz de `web/index.html` todavía debe cotejarse con el HTML íntegro de la APK original antes de afirmar que conserva todas las funciones. No se debe dar por validada la equivalencia funcional hasta completar esa revisión.
- No desinstales Manos Verdes Integral ni importes datos reales sin conservar antes una copia de seguridad.
