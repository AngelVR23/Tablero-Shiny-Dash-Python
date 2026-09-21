TABLERO DE DESARROLLO GLOBAL
============================

Descripcion
-----------
Dashboard interactivo para analizar el desarrollo socioeconomico de los paises
con datos del conjunto Gapminder. El tablero relaciona la poblacion, la
esperanza de vida y el PIB per capita para estudiar diferencias regionales y
la evolucion historica de cada pais.

Objetivo
--------
Facilitar la exploracion y comparacion de indicadores globales para apoyar el
analisis y la toma de decisiones basadas en datos.

Filtros disponibles
-------------------
- Continente o macro-region.
- Pais objetivo.
- Rango de anos de observacion.
- Metrica del mapa: PIB per capita o esperanza de vida.
- Metrica de tendencia: PIB per capita o esperanza de vida.

Visualizaciones
---------------
- Mapa geografico por pais, coloreado segun la metrica seleccionada.
- Comparacion de la nacion seleccionada contra el promedio continental y global.
- Evolucion historica de la metrica elegida.
- Top 10 de paises del continente seleccionado.
- Tarjetas KPI con poblacion, esperanza de vida y PIB per capita.

Unidades de medida
------------------
- Poblacion: habitantes.
- PIB per capita: USD por persona.
- Esperanza de vida: anos.
- Tiempo: anos calendario.

Fuente de datos
---------------
Los datos se cargan desde el conjunto Gapminder publicado en GitHub:
https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv

Tecnologias utilizadas
----------------------
- Python 3.12 o superior.
- Dash.
- Dash Bootstrap Components.
- Plotly Express.
- Pandas.
- NumPy.

Instalacion
-----------
Desde la carpeta del proyecto, instalar las dependencias con:

pip install -r requirements.txt

Ejecucion
---------
Ejecutar el archivo principal:

python dash-clase.py

El dashboard se inicia en:

http://127.0.0.1:8052/

Si el puerto 8052 esta ocupado, se debe liberar el puerto o modificar el
valor de port en dash-clase.py antes de iniciar la aplicacion.

Uso
---
1. Seleccionar un continente.
2. Elegir un pais de la region.
3. Definir el rango de anos.
4. Cambiar las metricas de los graficos cuando sea necesario.
5. Comparar los resultados del pais con los promedios regionales y globales.

Archivo principal
-----------------
- dash-clase.py: contiene la carga de datos, el layout, los callbacks y el
	servidor Dash.

Proyecto desarrollado para la asignatura Toma de decisiones basadas en datos.
