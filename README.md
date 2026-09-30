# Asistente del convenio

Chatbot que responde preguntas de los trabajadores (licencias, vacaciones, permisos...) usando únicamente el texto del convenio colectivo y citando el artículo.

## Estructura del repositorio

```
asistente-convenio/
├── app.py
├── system_prompt.txt
├── requirements.txt
├── README.md
└── data/
    └── convenio.pdf      (o convenio.txt)
```

## Puesta en marcha

1. **Crea un repositorio en GitHub** y sube estos archivos. Añade el convenio en `data/convenio.pdf` (o `data/convenio.txt`).
   - Si el PDF es un escaneo (imagen), no se podrá extraer el texto: usa un PDF con texto seleccionable o pásalo a `.txt`.
2. **Consigue una clave de API** en console.anthropic.com.
3. **Despliega en Streamlit Community Cloud** (share.streamlit.io, iniciando sesión con GitHub): elige el repositorio, la rama y `app.py`.
4. En **Advanced settings → Secrets**, pega:

```toml
ANTHROPIC_API_KEY = "tu-clave"
# Opcionales
ANTHROPIC_MODEL = "claude-sonnet-5-5"
APP_PASSWORD = "una-contraseña-para-la-demo"
```

La clave nunca debe ir dentro del código ni del repositorio.

## Probar en local

```bash
pip install -r requirements.txt
mkdir .streamlit
# crea .streamlit/secrets.toml con la clave (y añade esa carpeta a .gitignore)
streamlit run app.py
```

## Validación (para medir la calidad)

Prepara 15-20 preguntas típicas, anota la respuesta correcta según el convenio y comprueba cuántas acierta la app.

| # | Pregunta | Respuesta correcta (convenio) | Artículo | Respuesta de la app | ¿Correcta? | ¿Cita bien el artículo? |
|---|----------|-------------------------------|----------|---------------------|------------|-------------------------|
| 1 | ¿Cuántos días de licencia por matrimonio? | | | | | |
| 2 | ¿Cuántos días de vacaciones al año? | | | | | |
| 3 | ¿Licencia por fallecimiento de un familiar de primer grado? | | | | | |
| 4 | ¿Licencia por nacimiento de un hijo? | | | | | |
| 5 | ¿Permiso para acudir al médico? | | | | | |
| 6 | ¿Licencia por mudanza? | | | | | |
| 7 | ¿Permiso para exámenes oficiales? | | | | | |
| 8 | Pregunta cuya respuesta NO está en el convenio (debe derivar a RRHH) | | | | | |

Incluye siempre 2 o 3 preguntas trampa (fuera del convenio o ambiguas) para comprobar que la app no se inventa respuestas.

## Indicadores para la memoria del ejercicio

- Consultas recibidas por semana en RRHH sobre el convenio (antes).
- Tiempo medio por consulta (antes, por ejemplo 5-10 minutos) frente a segundos con la app.
- Porcentaje de aciertos en la validación.
- Porcentaje de preguntas que la app deriva correctamente a RRHH.

## Riesgos y mitigaciones

- **Respuestas erróneas:** cita obligatoria del artículo, aviso de que es orientativo y derivación a RRHH ante dudas.
- **Datos personales:** la app avisa de no introducirlos y no guarda el historial fuera de la sesión.
- **Convenio desactualizado:** sustituir el archivo de `data/` cuando haya revisión o prórroga.
- **Coste de la API:** límite de preguntas por sesión, contraseña opcional y caché del convenio.
