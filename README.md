# Himalayan Expeditions Data Visualization

## Autor
Claude 3.7 Sonnet

## Descripción del Proyecto
Este proyecto implementa un sistema interactivo multi-vista de visualización de datos que proporciona información sobre expediciones al Himalaya, permitiendo a los usuarios explorar patrones y relaciones entre rutas, picos, tasas de éxito, países y características de las expediciones.

## Objetivos
El sistema responde a las siguientes preguntas clave:

1. **Rutas y tasas de éxito**: ¿Qué rutas tienen las tasas de éxito más altas y más bajas para diferentes picos?
2. **Expediciones por país**: ¿Qué países han liderado más expediciones en diferentes períodos de tiempo?
3. **Duración y éxito**: ¿Las expediciones más largas tienen una mayor probabilidad de alcanzar la cumbre con éxito para cada pico? ¿Esto cambia según la temporada?
4. **Razones de terminación**: ¿Cómo han evolucionado las razones de terminación a lo largo de los años para cada pico?

## Estructura del Proyecto

- `/docs/`: Documentación del proyecto
  - `PRD.md`: Documento de Requisitos del Producto
  - `himalaya_data_dictionary.md`: Diccionario de datos que describe los conjuntos de datos

- `/input_data/`: Datos de entrada
  - `exped_tidy.csv`: Información de expediciones
  - `peaks_tidy.csv`: Información de picos montañosos
  - `unique_peaks_coords.csv`: Coordenadas geográficas de los picos

- `/output_data/`: Archivos generados
  - `himalayan_expeditions_analysis.ipynb`: Notebook con análisis y documentación del proceso de diseño
  - `app.py`: Aplicación Streamlit para las visualizaciones interactivas

## Características del Sistema de Visualización

### 1. Vista General
- Mapa interactivo de picos del Himalaya
- Gráficos de tendencias históricas de expediciones y tasas de éxito
- Estadísticas comparativas entre diferentes picos

### 2. Rutas y Tasas de Éxito
- Visualizaciones de tasas de éxito por ruta para cada pico
- Comparación de rutas entre diferentes montañas
- Análisis detallado de tasas de éxito con información contextual

### 3. Expediciones por País
- Evolución temporal de expediciones lideradas por diferentes países
- Vista apilada de la composición de expediciones por década
- Análisis específico de países para cada pico seleccionado

### 4. Duración y Éxito
- Análisis de la relación entre duración de expediciones y tasas de éxito
- Visualización de cómo esta relación varía por temporada
- Comparación entre diferentes picos y distribución de duraciones

### 5. Razones de Terminación
- Evolución de las razones de terminación a lo largo del tiempo
- Análisis de tendencias específicas para cada motivo de terminación
- Comparación de razones de terminación entre diferentes picos

## Cómo Ejecutar el Proyecto

### Requisitos
- Python 3.7 o superior
- Bibliotecas requeridas: pandas, numpy, altair, streamlit

### Instalación
1. Clone el repositorio o descomprima el archivo ZIP
2. Instale las dependencias requeridas:
   ```
   pip install pandas numpy altair streamlit
   ```

### Ejecución del Notebook
Para ejecutar el notebook de análisis:
1. Inicie Jupyter Notebook o Google Colab
2. Abra el archivo `output_data/himalayan_expeditions_analysis.ipynb`
3. Ejecute las celdas secuencialmente para ver el análisis y las visualizaciones

### Ejecución de la Aplicación Streamlit
Para ejecutar la aplicación interactiva:
1. Navegue al directorio del proyecto
2. Ejecute el siguiente comando:
   ```
   streamlit run output_data/app.py
   ```
3. La aplicación se abrirá automáticamente en su navegador web predeterminado

## Proceso de Diseño

El proceso de diseño del sistema de visualización se documenta en detalle en el notebook `himalayan_expeditions_analysis.ipynb`, que incluye:

- Proceso de limpieza de datos (300 palabras)
- Diseño de visualización para cada pregunta (300 palabras cada una)
- Diseño del sistema multi-vista integrado (500 palabras)
- Instrucciones paso a paso para resolver cada tarea

## Uso del Sistema

### Filtros y Controles
- Selector de pico montañoso
- Rango de años para filtrar datos
- Selector de temporada para análisis de duración

### Exploración Interactiva
- Interacción entre visualizaciones coordinadas
- Tooltips detallados con información contextual
- Selección y resaltado de elementos específicos

### Resolución de Preguntas
Cada pestaña del dashboard está diseñada para responder una de las preguntas clave:
1. **Vista General**: Proporciona contexto general sobre los picos y expediciones
2. **Rutas y Éxito**: Muestra qué rutas tienen las tasas de éxito más altas/bajas
3. **Países**: Analiza qué países han liderado más expediciones en diferentes períodos
4. **Duración y Éxito**: Explora la relación entre duración y probabilidad de éxito
5. **Razones de Terminación**: Muestra la evolución de razones de terminación por pico

## Conclusiones

Este sistema de visualización ofrece una plataforma completa para explorar y analizar datos de expediciones al Himalaya, permitiendo a los usuarios descubrir patrones, tendencias y relaciones que podrían no ser evidentes en los datos brutos. Las visualizaciones interactivas facilitan la investigación de preguntas específicas mientras se mantiene el contexto general, proporcionando información valiosa para investigadores, entusiastas del montañismo y analistas de datos.
