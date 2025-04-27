"""Functions for the ingestion and preprocessing of the documents for the vectorial base"""
import os
import glob
from typing import List, Optional

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def get_document_count(directory: str) -> int:
    """
    Count documents in Chroma vectorstore.
    
    Args:
        directory: Path to the vectorstore.
    
    Returns:
        int: Number of documents in the vectorstore.
    """
    try:
        chroma_files = glob.glob(os.path.join(directory, "*.parquet"))
        return len(chroma_files)
    except (OSError, IOError):
        return 0

def load_documents(directory: Optional[str] = None) -> List[Document]:
    """
    Load documents from a directory

    Args:
        directory: Path to the directory containing the documents
    Return:
        List[Document]: List of documents
    """
    if directory is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        directory = os.path.join(base_dir, "data", "documents")

    documents = []
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        create_sample_documents(directory)

    for file_path in glob.glob(os.path.join(directory, "**/*.*"), recursive=True):
        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif ext == ".txt":
                loader = TextLoader(file_path)
                documents.extend(loader.load())
            elif ext in [".csv", ".tsv"]:
                loader = CSVLoader(file_path)
                documents.extend(loader.load())
            elif ext in [".docx", ".doc"]:
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())

        except (OSError, ValueError, IOError) as e:
            print(f"Error al cargar {file_path}: {str(e)}")

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        documents = text_splitter.split_documents(documents)
    return documents

def create_sample_documents(directory: str) -> None:
    """
    Create sample documents with a basic financial information
    Args:
        directory: Path where the documents will be saved
    """
    ratios_content = """# Ratios Financieros Fundamentales

    Los ratios financieros son herramientas de análisis que permiten evaluar la salud financiera de una empresa.

    ## Ratios de Liquidez

    ### Ratio de Liquidez Corriente
    Fórmula: Activo Corriente / Pasivo Corriente
    Interpretación: Mide la capacidad de una empresa para pagar sus obligaciones a corto plazo. Un ratio superior a 1 indica que la empresa puede cubrir sus deudas a corto plazo.

    ### Ratio de Prueba Ácida
    Fórmula: (Activo Corriente - Inventarios) / Pasivo Corriente
    Interpretación: Similar al ratio de liquidez corriente, pero excluye los inventarios que pueden ser difíciles de convertir en efectivo.

    ## Ratios de Rentabilidad

    ### Margen de Beneficio Neto
    Fórmula: Beneficio Neto / Ventas Netas * 100
    Interpretación: Indica qué porcentaje de las ventas se convierte en beneficio después de todos los gastos.

    ### ROE (Return on Equity)
    Fórmula: Beneficio Neto / Patrimonio Neto * 100
    Interpretación: Mide la rentabilidad que obtienen los accionistas sobre su inversión en la empresa.

    ### ROA (Return on Assets)
    Fórmula: Beneficio Neto / Activos Totales * 100
    Interpretación: Indica la eficiencia con la que una empresa utiliza sus activos para generar beneficios.

    ## Ratios de Endeudamiento

    ### Ratio de Endeudamiento
    Fórmula: Pasivo Total / Activo Total * 100
    Interpretación: Muestra qué porcentaje de los activos está financiado con deuda.

    ### Ratio de Cobertura de Intereses
    Fórmula: EBIT / Gastos por Intereses
    Interpretación: Mide la capacidad de la empresa para pagar los intereses de su deuda con los beneficios operativos.
    """

    market_content = """# Conceptos Básicos del Mercado de Valores

    ## ¿Qué es una acción?
    Una acción representa una parte del capital social de una empresa. Al comprar una acción, se adquiere una pequeña parte de la propiedad de la empresa y el derecho a recibir dividendos si la empresa los distribuye.

    ## Tipos de Análisis de Acciones

    ### Análisis Fundamental
    El análisis fundamental evalúa el valor intrínseco de una empresa basándose en factores económicos, financieros y otros factores cualitativos y cuantitativos. Este enfoque examina los estados financieros, la posición competitiva, la gestión, las perspectivas de crecimiento y el entorno macroeconómico.

    ### Análisis Técnico
    El análisis técnico estudia los patrones de precios históricos y el volumen de negociación para predecir movimientos futuros. Se basa en la idea de que los precios se mueven en tendencias y que la historia tiende a repetirse.

    ## Indicadores de Mercado

    ### Índices Bursátiles
    Los índices bursátiles, como el S&P 500, el Dow Jones o el IBEX 35, son indicadores que muestran el comportamiento de un grupo de acciones representativas de un mercado o sector.

    ### Capitalización Bursátil
    La capitalización bursátil es el valor total de mercado de las acciones en circulación de una empresa. Se calcula multiplicando el precio actual de la acción por el número de acciones en circulación.

    ## Estrategias de Inversión

    ### Value Investing
    Estrategia que busca acciones infravaloradas según su valor intrínseco.

    ### Growth Investing
    Estrategia centrada en empresas con alto potencial de crecimiento.

    ### Income Investing
    Enfocada en la obtención de ingresos recurrentes a través de dividendos.
    """


    statements_content = """# Estados Financieros Básicos

    Los estados financieros proporcionan información esencial sobre la situación financiera y el rendimiento de una empresa.

    ## Balance General (Estado de Situación Financiera)

    El balance general muestra los activos, pasivos y patrimonio de una empresa en un momento específico.

    ### Activos
    Los activos son recursos controlados por la empresa como resultado de eventos pasados y de los cuales se espera obtener beneficios económicos futuros.

    - **Activos Corrientes**: Recursos que se espera convertir en efectivo o utilizar en un período menor a un año (efectivo, cuentas por cobrar, inventarios).
    - **Activos No Corrientes**: Recursos a largo plazo (propiedades, planta y equipo, inversiones a largo plazo).

    ### Pasivos
    Los pasivos son obligaciones presentes de la empresa, surgidas de eventos pasados, cuya liquidación se espera que resulte en una salida de recursos.

    - **Pasivos Corrientes**: Obligaciones que deben pagarse en un período menor a un año (cuentas por pagar, préstamos a corto plazo).
    - **Pasivos No Corrientes**: Obligaciones a largo plazo (deuda a largo plazo, obligaciones por pensiones).

    ### Patrimonio
    El patrimonio representa los derechos de los propietarios sobre los activos de la empresa después de deducir todos los pasivos.

    ## Estado de Resultados (Cuenta de Pérdidas y Ganancias)

    El estado de resultados muestra los ingresos, gastos y beneficios o pérdidas de una empresa durante un período específico.

    ### Componentes principales:
    - **Ingresos**: Incrementos en los beneficios económicos durante el período (ventas, ingresos por servicios).
    - **Costo de Ventas**: Costo directo de los bienes vendidos o servicios prestados.
    - **Gastos Operativos**: Gastos necesarios para el funcionamiento del negocio (administración, ventas, marketing).
    - **EBITDA**: Beneficio antes de intereses, impuestos, depreciación y amortización.
    - **EBIT**: Beneficio antes de intereses e impuestos.
    - **Beneficio Neto**: Resultado final después de restar todos los gastos de los ingresos.

    ## Estado de Flujos de Efectivo

    Muestra cómo los cambios en los balances y los ingresos afectan al efectivo y equivalentes de efectivo.

    ### Secciones:
    - **Flujos de efectivo de actividades operativas**: Efectivo generado por las operaciones principales del negocio.
    - **Flujos de efectivo de actividades de inversión**: Efectivo utilizado en la adquisición o venta de activos a largo plazo.
    - **Flujos de efectivo de actividades de financiación**: Efectivo relacionado con la financiación de la empresa (préstamos, dividendos).
    """

    with open(os.path.join(directory, "ratios_financieros.txt"), "w", encoding="utf-8") as f:
        f.write(ratios_content)

    with open(os.path.join(directory, "mercado_valores.txt"), "w", encoding="utf-8") as f:
        f.write(market_content)

    with open(os.path.join(directory, "estados_financieros.txt"), "w", encoding="utf-8") as f:
        f.write(statements_content)

    print(f"Documentos de ejemplo creados en {directory}")
