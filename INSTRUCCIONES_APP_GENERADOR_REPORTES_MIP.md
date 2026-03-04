# Instrucciones para Generador de Reportes MIP — App Web

## 1. Contexto General

**Empresa:** Sanitas Ambiental (control de plagas, certificada ISO 9001/14001/45001).

**Objetivo:** App web de uso interno (localhost) que permita, a partir de los informes de visita en PDF generados por el sistema actual, generar el **Informe MIP Mensual** consolidado — el documento que resume todas las visitas del mes para un cliente/sucursal.

**Usuarios:** Personal interno de Sanitas Ambiental (quien arma los reportes).

**Flujo general:** Subir PDFs de visitas del mes → la app parsea y extrae datos → el usuario completa datos faltantes (ej: conteo de voladores) → se genera el Informe MIP Mensual en PDF y Word.

---

## 2. Archivos de Entrada

Se reciben **dos tipos** de PDFs por visita, más pueden haber múltiples visitas por mes por cliente/sucursal.

### 2.1 Archivo tipo "Conforme" (Informe de visita)

- **Nombre ejemplo:** `Conforme124931_-_Visita_Regular.pdf`
- **Contenido:** Un PDF por visita con la siguiente estructura:
  - **Encabezado:** Logo Sanitas, nombre del cliente, dirección, Track ID.
  - **Datos del operario:** Fecha, nombre, hora ingreso, hora egreso.
  - **Detalle del Servicio** (hasta 3 bloques por visita):
    - **Desinsectación de Rastreros:** Tipo, modo (preventiva/correctiva/no realizado), maquinarias, producto, avistamiento (sí/no), comentarios.
    - **Desinsectación de Mosquitos (Voladores):** Tipo, modo, producto, avistamiento, comentarios.
    - **Desratización:** Tipo, modo (MIP), consumo (número), avistamiento, reposición (número), capturas (número), observaciones.
  - **Conforme de Servicio:** Nombre, apellido, DNI, puesto del receptor + firma.
  - **Relevamientos (Desvíos Fotográficos):** Sección con fotos embebidas en el PDF. Cada foto tiene: tipo de avistamiento, sector, descripción. Las fotos corresponden a desvíos de cualquiera de los tres servicios (rastreros, voladores, roedores).

### 2.2 Archivo tipo "MIP" (Registro detallado de roedores)

- **Nombre ejemplo:** `MIP_CALSA_-_Planta_4_2026-01-23.pdf`
- **Contenido:** Un PDF por visita de desratización con:
  - **Dashboard resumen:** Total consumos, capturas, reposiciones, cantidad de operarios.
  - **Productos utilizados** y comentarios generales.
  - **Tabla de Registros de Consumos:** ID, operario, insumo, punto de control (ej: CB004), cantidad, fecha, comentario.
  - **Tabla de Registros de Capturas:** Misma estructura que consumos.
  - **Tabla de Registros de Reposiciones:** ID, operario, insumo, tipo de reposición (consumo/degradado/mantenimiento/faltante), punto de control, cantidad, fecha.
  - **Relevamiento Original (tabla completa punto por punto):** Dividido en EXTERIORES e INTERIORES. Cada fila: subsección, código (CB001, CB002...), herramienta (Cebadera CB/PG), estado (Sin Novedad/Activa/Bloqueada/No Relevado), consumos, capturas, reposiciones, tipo reposición, operario, comentario.
  - **Firma de conformidad** del receptor.

### 2.3 Reglas sobre los archivos

- Siempre son PDF con estructura consistente.
- Un cliente puede tener múltiples sucursales.
- Cada sucursal puede tener 1 o más visitas en el mes.
- Por cada visita hay un "Conforme" y un "MIP" de roedores.
- Los desvíos fotográficos siempre están embebidos dentro del PDF Conforme.
- Los gramos de consumo ya vienen calculados en el archivo MIP (no hay que aplicar una regla de conversión manual; el sistema ya hizo la cuenta según el producto).

---

## 3. Documento de Salida — Informe MIP Mensual

El resultado es un **único documento por cliente/sucursal/mes** que consolida todas las visitas. Se debe generar en **PDF y Word (.docx)**. La estructura debe seguir exactamente el ejemplo provisto (`Informe_MIP_-_Mensual_-_Planta_4_-_Enero_2026.pdf`).

### 3.1 Estructura del Informe Mensual

#### A. Portada / Encabezado
- Logo Sanitas Ambiental + certificaciones ISO (9001, 14001, 45001).
- Título: "INFORME MIP"
- Cliente (nombre completo).
- Mes del informe.
- Dirección de la sucursal.

#### B. Sección: Control de Roedores
1. **Datos generales:**
   - Sector (ej: "Planta 4").
   - Cantidad de estaciones: Perímetro Externo (X und), Perímetro Interno (X und).

2. **Tabla de Desvíos del mes:**
   - Columnas: Fecha | Observaciones.
   - Una fila por cada visita del mes, extrayendo las observaciones de la sección Desratización de cada Conforme.
   - Si una visita tiene referencia a desvío fotográfico, indicar "- Referencia" al final de la observación.

3. **Desvíos Fotográficos de Roedores:**
   - Debajo de la tabla, insertar las fotos extraídas de los Conformes que correspondan a roedores.
   - Cada foto con su sector y descripción.
   - En la tabla de observaciones, hacer referencia cruzada a estas fotos.

4. **Gráfico: Registros de Consumos por Sector:**
   - Gráfico de barras.
   - Eje X: Sectores (Perímetro Externo, Perímetro Interno, etc.).
   - Eje Y: Consumos en gramos (gr).
   - Los datos se consolidan sumando todos los consumos de todas las visitas del mes, agrupados por sector/subsección.

5. **Registro de Capturas:**
   - Tarjetas/cards mostrando: Número de ranking, código de cebadera, tipo (Cebadera PG/CB), sector, cantidad de capturas.
   - Solo mostrar las que tuvieron capturas.

6. **Ranking: Estaciones con Desvíos (Top 10 Consumo de Cebos):**
   - Lista tipo ranking (1 a 10).
   - Cada item: Número, código cebadera, tipo (Cebadera CB/PG), sector, consumo en gr.
   - Ordenado de mayor a menor consumo.
   - Datos consolidados de todas las visitas del mes.

7. **Gráfico: Reposiciones por tipo:**
   - Gráfico mostrando reposiciones clasificadas por tipo: Consumo / Degradado / Mantenimiento / Faltante.
   - Sirve como referencia del gasto en insumos.

8. **Registros de Producto Utilizado:**
   - Lista de productos usados durante el mes para roedores (ej: "Gel Tek Rodenticida", "Placa de Pegamento Pega Rat").

9. **Resumen de Tratamiento (Roedores):**
   - Texto narrativo resumiendo la situación del mes para roedores.
   - Debe mencionar: acciones realizadas, desvíos encontrados, medidas correctivas aplicadas, recomendaciones.
   - Debe hacer referencia a los desvíos fotográficos.

#### C. Sección: Control de Voladores
1. **Datos generales:**
   - Cantidad de trampas UV: Perímetro Interno (X und).

2. **Tabla de observaciones del mes:**
   - Columnas: Fecha | Observaciones.
   - Extraídas de la sección "Desinsectación de Mosquitos" de cada Conforme del mes.

3. **Desvíos Fotográficos de Voladores:**
   - Si existen fotos de desvíos relacionadas a voladores, insertarlas aquí con sector y descripción.

4. **Formulario de Carga Manual (Conteo de capturas por trampa UV):**
   - **Este es un componente interactivo de la app, NO del PDF final.**
   - El usuario debe poder configurar:
     - Cantidad de trampas (ej: 9 trampas, TUV01 a TUV09).
     - Especies/plagas a relevar (ej: Moscas, Mosca de la Fruta, Plodia, Carcoma — configurables, se pueden agregar o quitar).
   - Luego, el usuario ingresa manualmente la cantidad de cada especie capturada por trampa.
   - Con estos datos se genera el gráfico.

5. **Gráfico: Capturas por Trampa UV:**
   - Gráfico de barras agrupadas/stacked.
   - Eje X: Trampas (TUV01, TUV02, TUV03...).
   - Eje Y: Cantidad de individuos.
   - Barras por especie (cada especie con color diferente).
   - Leyenda con las especies.

6. **Resumen de Tratamiento (Voladores):**
   - Texto narrativo resumiendo la situación de voladores del mes.
   - Mencionar: recambios de placas, equipos fuera de servicio/bloqueados, tendencias de capturas, recomendaciones.
   - Referencia a desvíos fotográficos si existen.

#### D. Sección: Control de Insectos Rastreros
1. **Datos generales:**
   - Perímetro Externo / Perímetro Interno (si aplica).

2. **Tabla de aplicaciones del mes:**
   - Columnas: Fecha | Producto | Laboratorio | Principio Activo | Dosis | Cantidad Aplicada | Sectores Tratados.
   - Una fila por cada visita donde se realizó desinsectación de rastreros.
   - Datos extraídos de los Conformes.

3. **Desvíos Fotográficos de Rastreros:**
   - Si existen fotos de desvíos de rastreros, insertarlas aquí.

4. **Resumen de Tratamiento (Rastreros):**
   - Texto narrativo: productos usados, sectores tratados, desvíos (si hubo), recomendaciones.

#### E. Conclusión General
- Texto que consolida los tres servicios.
- Debe contener:
  - Referencia al período evaluado (mes/año).
  - Referencia a cada tipo de control con sus desvíos, acciones tomadas y recomendaciones.
  - Sección final para recomendaciones de **exclusión e higiene** (separada o destacada).
  - Mención de que los relevamientos fotográficos, HDS y certificados de productos están disponibles en el portal web.

---

## 4. Funcionalidades de la App Web

### 4.1 Pantalla Principal / Dashboard
- Selección o creación de cliente.
- Selección de sucursal (un cliente puede tener varias).
- Selección de mes/año del informe.

### 4.2 Carga de Archivos
- Zona de drag & drop para subir múltiples PDFs.
- La app debe identificar automáticamente si es un "Conforme" o un "MIP" (por el contenido/estructura del PDF).
- Mostrar lista de archivos cargados con su tipo detectado, fecha y Track ID.
- Permitir eliminar o agregar archivos.
- Validación: avisar si falta un MIP para un Conforme que tiene desratización, o viceversa.

### 4.3 Parseo / Extracción de Datos
Al procesar los PDFs, la app debe extraer:

**Del Conforme:**
- Cliente, dirección, Track ID, fecha, operario, horarios.
- Para cada tipo de servicio: todos los campos (tipo, modo, producto, avistamiento, comentarios/observaciones, y para roedores: consumo, reposición, capturas).
- Receptor del servicio (nombre, DNI, puesto).
- Imágenes de relevamientos/desvíos (extraer las fotos embebidas) con su sector y descripción.

**Del MIP:**
- Dashboard resumen (consumos totales, capturas, reposiciones).
- Tablas de consumos, capturas, reposiciones (punto por punto).
- Tabla de relevamiento original completo (estado de cada cebadera).
- Productos utilizados.

### 4.4 Vista de Revisión / Edición y Consulta de Datos Faltantes
Después del parseo, la app debe:

1. **Detectar campos vacíos o faltantes:** No todos los informes traen todos los datos (ej: dosis, laboratorio, principio activo, cantidades aplicadas pueden faltar en algunos Conformes). La app debe identificar qué campos no pudo extraer.

2. **Consultar al usuario los datos faltantes:** Mostrar un panel/formulario claro que liste los datos que no se encontraron, organizados por visita y tipo de servicio. Ejemplo:
   - "Visita 14/01 — Rastreros: Falta **Producto**, **Dosis**, **Cantidad Aplicada**. ¿Querés completarlos?"
   - "Visita 23/01 — Voladores: Falta **Laboratorio**, **Principio Activo**."
   
3. **Permitir completar inline:** El usuario puede llenar los campos faltantes directamente en la misma vista, sin tener que navegar a otro lugar.

4. **Permitir marcar como "No aplica":** Si el dato no existe o no corresponde, el usuario puede marcarlo como N/A para que no aparezca en el informe final.

5. **Verificación general:** Además de los faltantes, mostrar todos los datos extraídos para que el usuario pueda corregir errores de parseo o agregar información adicional.

### 4.5 Formulario de Voladores (Carga Manual)
- Componente dedicado donde el usuario configura:
  - **Cantidad de trampas** y sus códigos (TUV01, TUV02...).
  - **Especies a relevar** (lista configurable: Moscas, Mosca de la fruta, Plodia, Carcoma, etc. — se pueden agregar/quitar).
- Grilla/tabla editable: Filas = trampas, Columnas = especies.
- El usuario completa las cantidades manualmente (conteo físico de las placas UV).
- Con estos datos se genera automáticamente el gráfico de capturas.

### 4.6 Editor de Resúmenes y Conclusión
- Campos de texto enriquecido (o textarea) para que el usuario redacte o edite:
  - Resumen de Tratamiento de Roedores.
  - Resumen de Tratamiento de Voladores.
  - Resumen de Tratamiento de Rastreros.
  - Conclusión General.
- **Opción deseable:** Que la app pre-genere un borrador automático basado en los datos extraídos (ej: si hubo capturas, mencionarlo; si hubo equipos bloqueados, mencionarlo). El usuario luego edita.

### 4.7 Vista Previa del Informe
- Preview del documento final antes de generar.
- Incluir todos los gráficos renderizados.
- Incluir las fotos de desvíos en su ubicación correcta.

### 4.8 Generación del Documento Final
- Generar en **PDF** (respetando el estilo visual del ejemplo: colores Sanitas, encabezados teal, tablas con formato, gráficos embebidos).
- Generar en **Word (.docx)** (editable, con la misma estructura).
- Descarga directa desde la app.

---

## 5. Reglas de Negocio y Lógica

### 5.1 Consolidación de Datos de Roedores
- **Consumos por sector:** Sumar los consumos (en gr) de todas las visitas del mes, agrupados por subsección (Perímetro Externo, Perímetro Interno, etc.).
- **Ranking de cebaderas:** Sumar consumos por punto de control (CB001, CB002...) de todas las visitas, ordenar de mayor a menor, mostrar Top 10.
- **Capturas:** Consolidar capturas de todas las visitas. Mostrar solo cebaderas con capturas > 0.
- **Reposiciones por tipo:** Clasificar y sumar todas las reposiciones del mes por tipo (Consumo / Degradado / Mantenimiento / Faltante).
- **Gramos:** Los gramos ya vienen calculados en el archivo MIP. No se necesita aplicar fórmula de conversión.

### 5.2 Voladores
- Los datos de capturas por trampa se cargan manualmente vía formulario.
- Los datos de observaciones por fecha se extraen de los Conformes.

### 5.3 Rastreros
- La tabla de aplicaciones se arma extrayendo los datos de producto de cada Conforme donde se realizó desinsectación de rastreros (modo ≠ "No realizado").

### 5.4 Desvíos Fotográficos
- Extraer todas las imágenes de la sección "Relevamientos" de los Conformes.
- Clasificarlas por tipo de plaga según el contexto (sector mencionado, descripción).
- Insertarlas debajo de la sección correspondiente en el informe final.
- En las tablas de observaciones, donde corresponda, agregar referencia al desvío fotográfico.

### 5.5 Visitas "No realizado"
- Si una visita tiene un servicio como "No realizado" (ej: Conforme126257 donde rastreros y mosquitos fueron "No realizado"), no incluir esa visita en las tablas de ese servicio, pero sí incluirla en el servicio que sí se realizó (en ese caso, desratización).

### 5.6 Manejo de Datos Faltantes
- **Regla general:** Si un dato requerido para el informe final no se encuentra en el PDF, la app NUNCA debe inventarlo o dejarlo en blanco silenciosamente. Siempre debe consultarle al usuario.
- **Datos que pueden faltar frecuentemente:** Dosis, laboratorio, principio activo, cantidad aplicada (en rastreros); cantidad de trampas UV, especies relevadas (en voladores); cantidad de estaciones por perímetro.
- **Flujo:** Parseo → Detección de faltantes → Panel de consulta al usuario → El usuario completa → Recién ahí se habilita la generación del informe.
- **Indicador visual:** Los campos faltantes deben mostrarse resaltados (ej: borde rojo o etiqueta "Dato pendiente") para que el usuario los identifique rápido.

---

## 6. Stack Tecnológico Sugerido

Dado que es una app interna en localhost:

- **Frontend:** React (con Tailwind CSS para estilos).
- **Backend:** Node.js con Express, o Python con Flask/FastAPI.
- **Parseo de PDFs:** Librería de extracción de texto y imágenes de PDF (ej: `pdf-parse`, `pdfjs-dist` para JS; `PyMuPDF`/`fitz` o `pdfplumber` para Python).
- **Generación de PDF:** `puppeteer` (renderizar HTML a PDF) o librerías específicas.
- **Generación de Word:** `docx` (librería JS) o `python-docx`.
- **Gráficos:** `Chart.js` o `Recharts` en frontend para preview; para el documento final, renderizar como imagen e insertar.
- **Base de datos (opcional):** SQLite para guardar informes generados si se quiere historial.

---

## 7. Flujo de Uso Paso a Paso

1. El usuario abre la app en localhost.
2. Selecciona o crea el cliente y sucursal.
3. Selecciona el mes/año.
4. Sube todos los PDFs del mes (Conformes + MIPs).
5. La app parsea los PDFs y muestra los datos extraídos.
6. El usuario revisa y corrige si es necesario.
7. El usuario completa el formulario de voladores (capturas por trampa UV).
8. El usuario completa o edita los campos de datos generales (cant. estaciones perímetro externo/interno, cant. trampas UV, etc.) si no se extrajeron automáticamente.
9. El usuario redacta/edita los resúmenes de tratamiento y la conclusión general (con borrador automático opcional).
10. Vista previa del informe completo.
11. Genera y descarga el informe en PDF y/o Word.

---

## 8. Consideraciones Adicionales

- **Estilo visual:** Respetar los colores y diseño de Sanitas Ambiental (teal/verde azulado para encabezados, tipografía limpia, tablas con headers de color).
- **Múltiples sucursales:** Un cliente puede tener Planta 1, Planta 2, etc. Cada sucursal genera su propio informe mensual independiente.
- **Escalabilidad:** La estructura debe soportar agregar nuevos tipos de plagas o secciones en el futuro.
- **Sin autenticación necesaria** (es localhost, uso interno).
- **Datos sensibles:** Los PDFs contienen DNI y firmas del receptor. No se exponen fuera de localhost.
