# FinBot - Asistente de Análisis Financiero

Un agente de IA con arquitectura RAG y herramientas especializadas para análisis financiero.

## Descripción del Proyecto

FinBot es un asistente inteligente que puede responder preguntas sobre datos financieros de empresas que cotizan en bolsa. Utiliza una combinación de:

1. **Sistema RAG (Retrieval-Augmented Generation)** para acceder a conocimiento financiero general
2. **API Financiera** para consultar datos actualizados del mercado (Yahoo Finance)
3. **Calculadora Financiera** para realizar cálculos especializados

Este proyecto demuestra cómo construir un agente que puede decidir dinámicamente cuándo utilizar cada herramienta según la consulta del usuario.

## Características

- 🤖 **Agente inteligente** basado en LangChain con arquitectura ReAct
- 📚 **Base de conocimiento** con información financiera general
- 📊 **Consulta de datos en tiempo real** para empresas que cotizan en bolsa
- 🧮 **Cálculos financieros avanzados** (ROI, VAN, TIR, ratios, préstamos, etc.)
- 💻 **Interfaz de consola** fácil de usar
- 🌐 **Interfaz web** basada en Streamlit

## Requisitos

- Python 3.12 o superior
- Dependencias listadas en `requirements.txt`
- Clave API de OpenAI (para el LLM)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/betochalo/finbot.git
   cd finbot
   ```

2. Crear un entorno virtual y activarlo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Crear un archivo `.env` con las variables de entorno necesarias:
   ```
   # LLM Provider OpenAI
   LLM_PROVIDER=openai
   OPENAI_API_KEY=tu_clave_api_aqui
   
   # Configuración LLM
   MODEL_PROVIDER=gpt-4
   
   
   # Embeddings
   EMBEDDINGS_PROVIDER=openai
   OPENAI_EMBEDDINGS_MODEL=model_name
   # O para embeddings locales:
   # EMBEDDINGS_PROVIDER=local
   # SENTENCE_TRANSFORMERS_MODEL=all-MiniLM-L6-v2

   ```

## Uso

### Iniciar la interfaz web (Streamlit):

```bash
streamlit run src/ui/web.py
```

## Ejemplos de consultas

- Preguntas sobre conceptos financieros:
  - "¿Qué es el ratio de liquidez corriente?"
  - "Explícame cómo se calcula el ROA"

- Consultas sobre empresas:
  - "Muéstrame información actual sobre Apple"
  - "¿Cuál es el precio de las acciones de Microsoft?"
  - "¿Cuáles son los estados financieros de Tesla?"

- Cálculos financieros:
  - "Calcula el ROI de una inversión de $5000 que ahora vale $7500"
  - "Calcula el pago mensual de un préstamo de $20000 al 6% a 4 años"
  - "¿Cuál es el VAN de un proyecto con una inversión inicial de $10000 y flujos de $4000, $5000 y $6000 en los siguientes años con una tasa del 8%?"

## Arquitectura

```
Usuario → Agente LLM → Decisión:
                       ├─→ RAG → Consulta base vectorial → Respuesta
                       │    (Para información general, definiciones, etc.)  
                       │
                       └─→ Tools → Llamada a API/Calculadora → Respuesta
                            (Para datos actualizados o cálculos específicos)
```

## Herramientas incluidas

1. **Base de Conocimiento RAG**:
   - Información sobre conceptos financieros, ratios, mercado de valores, etc.
   - Utiliza embeddings y una base vectorial (Chroma)

2. **API Financiera** (Yahoo Finance):
   - Información general de empresas
   - Precios actuales e históricos
   - Estados financieros

3. **Calculadora Financiera**:
   - ROI (Retorno sobre Inversión)
   - Interés compuesto
   - Amortización de préstamos
   - Ratios financieros
   - VAN (Valor Actual Neto)
   - TIR (Tasa Interna de Retorno)

## Posibles mejoras futuras

- Integración con más fuentes de datos financieros
- Visualización de datos y gráficos
- Análisis de sentimiento de noticias financieras
- Sugerencias personalizadas basadas en perfiles de inversión
- Implementación de modelos de pronóstico

## Colaboradores

- [Roberth Chachalo](https://github.com/betochalo)