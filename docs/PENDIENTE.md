# Tareas Pendientes y Próximas Mejoras

Este documento mantiene el registro de los próximos ajustes, bugs a corregir y nuevas funcionalidades a implementar en el Generador de Informes MIP.

## 🐛 Corrección de Errores (Bugs)
- [ ] **Visita vacía en roedores**: Solucionar el defasaje que genera que se muestre una visita vacía o sin datos en la tabla de observaciones de roedores.
- [ ] **Mapeo de "Otros Sectores" en Roedores**: Mejorar la lógica de búsqueda y mapeo en el archivo PDF del MIP. Aunque se muestran los consumos, hay que asegurar que se asignen al sector correcto en lugar de caer por defecto en "Otros Sectores / Ajuste".
- [ ] **Precisión en detalles de imágenes**: Ajustar la extracción y asociación de los detalles (sector, acción) de las fotografías para que sean mucho más precisos y coherentes con el texto del informe.

## ✨ Nuevas Funcionalidades (UI y Extracción)
- [ ] **Pre-completado inteligente en Rastreros**: Si la información de *dosis* y *cantidad de litros* aplicados está en el detalle del informe (Conforme), pre-completar esos campos automáticamente en la vista de revisión (`ReviewPage`). El usuario debe poder modificar estos valores o agregarlos manualmente si el PDF no los tenía.
- [ ] **Configuración de Metadatos del Informe** (Campos globales):
    - [ ] **Dirección del Cliente**: Agregar un campo al inicio (probablemente al subir el archivo o al inicio de la revisión) para indicar la dirección y que salga correctamente en el encabezado del PDF.
    - [ ] **Cantidad de Trampas UV**: Permitir setear este valor globalmente para que se agregue solo en el informe estructural de voladores.
    - [ ] **Cantidad de Cebaderas**: Permitir setear la cantidad de estaciones (Perímetro Externo / Interno) en algún lugar accesible para que se inyecten directamente en el PDF de roedores.

## 🎨 Ajustes de Plantilla PDF (`report.html`) y Textos
- [ ] **Ocultar detalle en Voladores**: Eliminar o de momento sacar la tabla de "Detalle de Capturas" en la sección de voladores. Con el gráfico de barras es suficiente.
- [ ] **Cambio de título en Rastreros**: Reemplazar el título "Tablas de Aplicaciones" por "Registro de Aplicaciones".

---
*Nota: El flujo de impresión continuo del PDF ya fue implementado y validado exitosamente.*
