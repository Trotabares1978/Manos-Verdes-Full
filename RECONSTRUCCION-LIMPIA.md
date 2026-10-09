# Manos Verdes Full — reconstrucción limpia

## Regla del proyecto
No reutilizar scripts que parcheen binarios APK ni asumir que un APK modificado está listo para instalar. Reconstruir una aplicación nueva a partir de la referencia funcional disponible y validar cada módulo.

## Requisitos
- Identificador Android independiente de Manos Verdes Integral para instalar ambas en paralelo.
- Mantener la estética y las funciones observables de la aplicación de referencia.
- Importar backups JSON existentes sin cambiar el esquema original; validar y normalizar los datos antes de guardarlos.
- Añadir botón de WhatsApp junto a cada pedido en la ruta que tenga teléfono.
- Permitir exportar un backup antes y después de la migración.
- No incluir secretos, claves privadas ni APK originales en el repositorio.

## Esquema de datos heredado detectado en la versión HTML de referencia
- mvi_orders
- mvi_history
- mvi_debts
- mvi_clients
- mvi_route_templates
- mvi_active_route
- mvi_products

## Criterios de aceptación
1. Compilación limpia desde el repositorio.
2. Identificador de paquete distinto al original.
3. Instalación en Android sin desinstalar Manos Verdes Integral.
4. Importación de un backup de referencia y comparación de recuentos/valores antes y después.
5. Validación de pedidos, pagos, entregas, deudas, stock, historial y rutas.
6. Botón WhatsApp solo cuando el pedido tenga teléfono; número normalizado y apertura de WhatsApp con mensaje editable.
7. Exportación de backup y restauración comprobadas en una instalación limpia.

## Bloqueo de entrada
La APK original debe estar disponible localmente como artefacto de entrada para poder comparar pantallas, manifiesto, recursos, comportamiento y esquema de almacenamiento. No subir la APK ni credenciales al repositorio.
