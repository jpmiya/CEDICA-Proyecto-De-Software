from datetime import datetime
from io import BytesIO
from typing import Dict, List

from flask import Blueprint, render_template, send_file
from fpdf import FPDF

from src.core.reports.reports import (
    get_ranking_proposals,
    get_riders_in_debt,
    get_riders_without_full_information,
)
from src.core.riders.rider import Rider
from src.web.handlers.auth import login_required, permission_required


bp = Blueprint("reports", __name__, url_prefix="/reportes")


def get_full_ranking():
    """
    Obtiene el ranking completo de propuestas, incluyendo aquellas que no tienen registros.

    Esta función obtiene los datos del ranking de propuestas desde la base de datos,
    y asegura que todas las propuestas posibles estén representadas en el ranking,
    incluso si no tienen registros. Las propuestas que no tienen registros se
    completan con un valor de 0.

    El ranking se ordena de mayor a menor según el número de registros.

    Returns:
        dict: Un diccionario donde las claves son las propuestas y los valores son el
              número de registros (conteo), ordenado de mayor a menor.
    """
    # Obtiene los datos desde la base de datos
    stored_ranking = get_ranking_proposals()  # Devuelve objetos con .proposal y .count
    # Lista de todas las propuestas
    all_proposals = [
        "Hipoterapia",
        "Monta Terapeutica",
        "Deporte Ecuestre Adaptado",
        "Actividades Recreativas",
        "Equitacion",
    ]

    # Convertir datos existentes en un diccionario
    stored_dict = {row.proposal: row.count for row in stored_ranking}
    # Completar con las propuestas que no tienen registros
    full_ranking: dict[str, int] = dict()
    for proposal in all_proposals:
        full_ranking[proposal] = stored_dict.get(proposal, 0)

    sorted_ranking = dict(
        sorted(full_ranking.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_ranking


def get_incomplete_riders() -> List[Dict[str, str]]:
    """
    Obtiene una lista de jinetes que tienen información incompleta en su registro.

    Esta función recupera los jinetes que no tienen información completa en sus registros,
    y organiza los datos en un formato de diccionario con campos clave como apellido, nombre,
    DNI, discapacidad, seguro, trabajo institucional y tutores. Los valores para discapacidad,
    seguro y tutores se establecen como "SI" o "NO" según la disponibilidad de los datos.

    La lista de jinetes se ordena por apellido de forma ascendente.

    Returns:
        List[dict]: Una lista de diccionarios, cada uno representando a un jinete, con
                    información clave sobre su registro. La lista está ordenada por apellido.
    """
    incomplete_riders: List[Rider] = get_riders_without_full_information()
    riders_data: List[Dict[str, str]] = []
    for rider in incomplete_riders:
        riders_data.append(
            {
                "last_name": rider.last_name,
                "first_name": rider.name,
                "dni": rider.dni,
                "disability": (
                    "NO"
                    if rider.disability_id is None or rider.benefit_id is None
                    else "SI"
                ),
                "insurance": (
                    "NO"
                    if rider.insurance_id is None or rider.school_id is None
                    else "SI"
                ),
                "institutional_work": (
                    "NO" if rider.institutional_work_id is None else "SI"
                ),
                "tutors": "NO" if rider.primary_tutor is None else "SI",
            }
        )
    riders_data = sorted(riders_data, key=lambda rider: rider["last_name"])

    return riders_data


@bp.get("/")
@login_required
@permission_required("report_index")
def index():
    """
    Muestra la página principal del reporte de ranking de propuestas.

    Esta función se encarga de renderizar la página de inicio para los reportes de
    ranking de propuestas. Requiere que el usuario esté autenticado y tenga el permiso
    correspondiente para acceder a la página.

    Returns:
        render_template: La plantilla 'index.html' que muestra la página principal
                         del reporte de ranking de propuestas.
    """
    return render_template("reports/index.html")


@bp.get("/ranking_propuestas")
@login_required
@permission_required("report_show")
def show_ranking_proposals():
    """
    Muestra el ranking completo de propuestas.

    Esta función genera el ranking completo de propuestas utilizando la función
    `get_full_ranking()` y renderiza la página correspondiente mostrando los datos
    del ranking. Requiere que el usuario esté autenticado y tenga el permiso necesario
    para visualizar los reportes.

    Returns:
        render_template: La plantilla 'ranking_proposals.html' que muestra el ranking
                         de propuestas generado.
    """
    # Generar el ranking completo
    ranking = get_full_ranking()

    return render_template("reports/ranking_proposals.html", ranking=ranking)


@bp.get("/ranking_propuestas/download")
@login_required
@permission_required("report_show")
def download_ranking():
    """
    Descarga el ranking completo de propuestas en formato PDF.

    Esta función genera un archivo PDF con el ranking completo de propuestas,
    incluyendo la fecha y hora de generación. El PDF se crea utilizando la biblioteca
    FPDF y se devuelve como un archivo descargable para el usuario. Requiere que
    el usuario esté autenticado y tenga el permiso correspondiente para descargar
    los reportes.

    Returns:
        send_file: El archivo PDF generado que contiene el ranking completo de propuestas.
    """
    # Generar el ranking completo
    ranking = get_full_ranking()

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Fecha y hora de generación
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y")
    pdf.cell(
        200,
        10,
        text=f"Ranking de Propuestas (Generado: {timestamp})",
        ln=True,
        align="C",
    )

    # Espaciado adicional antes de la tabla
    pdf.ln(10)

    # Encabezados de la tabla
    pdf.set_font("Arial", style="B", size=12)  # Negrita para encabezados
    pdf.cell(130, 10, "Propuesta", border=1, align="C")
    pdf.cell(50, 10, "Cantidad", border=1, align="C")
    pdf.ln(10)

    # Filas de la tabla
    pdf.set_font("Arial", size=12)  # Texto normal
    for propuesta, contador in ranking.items():
        proposal = propuesta
        count = str(contador)

        # Agregar los datos a la tabla
        pdf.cell(130, 10, proposal, border=1, align="L")
        pdf.cell(50, 10, count, border=1, align="C")
        pdf.ln(10)

    # Guardar el PDF en memoria
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(
        pdf_output, download_name="ranking_propuestas.pdf", as_attachment=True
    )


@bp.get("/jinetes_dedudores")
@login_required
@permission_required("report_show")
def show_riders_in_debt():
    """
    Muestra la lista de jinetes con deudas.

    Esta vista se encarga de obtener los jinetes con deudas a través de la
    función `get_riders_in_debt` y los pasa al template 'reports/riders_in_debt.html'
    para su visualización. Requiere que el usuario esté autenticado y tenga
    el permiso 'report_show'.
    """
    riders = get_riders_in_debt()

    return render_template("reports/riders_in_debt.html", riders=riders)


@bp.get("/jinetes_dedudores/download")
@login_required
@permission_required("report_show")
def download_riders_in_debt():
    """
    Descarga el reporte de jinetes con deudas en formato PDF.

    Esta vista genera un reporte en PDF con la lista de jinetes que tienen deudas.
    Los datos incluyen el apellido, nombre y DNI de cada jinete. El reporte se
    genera dinámicamente usando la librería FPDF y se retorna como un archivo PDF
    descargable. Requiere que el usuario esté autenticado y tenga el permiso 'report_show'.
    """
    riders: List[Rider] = get_riders_in_debt()

    # Crear el objeto FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Fecha y hora de generación
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y")
    pdf.cell(
        200,
        10,
        text=f"Reporte de Jinetes con Deudas (Generado: {timestamp})",
        ln=True,
        align="C",
    )

    # Título del PDF
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, text="Reporte de Jinetes con Deudas", ln=True, align="C")
    pdf.ln(10)  # Salto de línea

    # Encabezados de la tabla
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(60, 10, text="Apellido", border=1, align="C")
    pdf.cell(60, 10, text="Nombre", border=1, align="C")
    pdf.cell(60, 10, text="DNI", border=1, align="C")
    pdf.ln()  # Salto de línea para la fila siguiente

    # Contenido de la tabla
    pdf.set_font("Arial", size=12)
    for rider in riders:
        pdf.cell(60, 10, text=rider.last_name, border=1, align="L")
        pdf.cell(60, 10, text=rider.name, border=1, align="L")
        pdf.cell(60, 10, text=str(rider.dni), border=1, align="L")
        pdf.ln()  # Salto de línea para la fila siguiente

    # Generar el PDF en memoria
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    # Retornar el archivo como respuesta
    return send_file(
        pdf_output,
        as_attachment=True,
        download_name="Jinetes_deudores.pdf",
        mimetype="application/pdf",
    )


@bp.get("/jinetes_sin_info_completa")
@login_required
@permission_required("report_show")
def show_riders_without_full_information():
    """
    Muestra el reporte de jinetes con información incompleta.

    Esta función obtiene los datos de los jinetes que no tienen toda la información
    completa y los pasa a una plantilla para su visualización en la página web.
    Requiere que el usuario esté autenticado y tenga el permiso correspondiente
    para visualizar el reporte.

    Returns:
        render_template: La plantilla 'incomplete_riders.html' que muestra
                         los jinetes con información incompleta.
    """
    riders_data = get_incomplete_riders()

    return render_template("reports/incomplete_riders.html", riders=riders_data)


@bp.get("/jinetes_sin_info_completa/download")
@login_required
@permission_required("report_show")
def download_riders_without_full_information():
    """
    Descarga el reporte de jinetes con información incompleta en formato PDF.

    Esta función genera un archivo PDF con los jinetes que tienen información
    incompleta, mostrando los detalles como apellido, nombre, DNI, discapacidad,
    situación provisional, tutores y trabajo institucional. El archivo PDF se
    devuelve como una respuesta de descarga para el usuario. Requiere que el
    usuario esté autenticado y tenga el permiso correspondiente para descargar
    el reporte.

    Returns:
        send_file: El archivo PDF generado que contiene los jinetes con información
                   incompleta.
    """
    riders_data = get_incomplete_riders()  # Obtén los datos de riders incompletos

    # Configurar el PDF
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y")
    pdf.cell(
        200,
        10,
        text=f"Jinetes con información incompleta (Generado: {timestamp})",
        ln=True,
        align="C",
    )

    # Títulos de las columnas
    headers = [
        "Apellido",
        "Nombre",
        "DNI",
        "Discapacidad\ny pensiones",
        "Situación provisional\ny escolar",
        "Tutores",
        "Trabajo\ninstitucional",
    ]

    # Anchos personalizados para cada columna
    column_widths = [60, 60, 20, 30, 50, 30, 30]
    row_height = 10  # Altura de cada fila

    # Añadir encabezados usando multi_cell
    pdf.set_fill_color(200, 200, 200)
    y_start = pdf.get_y()
    for i, (header, width) in enumerate(zip(headers, column_widths)):
        x_start = pdf.get_x()
        pdf.multi_cell(width, row_height / 2, header, border=1, align="C", fill=True)
        pdf.set_xy(x_start + width, y_start)  # Volver al inicio para la siguiente celda

    pdf.ln(row_height)  # Pasar a la siguiente línea después de los encabezados

    # Añadir datos
    pdf.set_font("Arial", "", 10)
    for rider in riders_data:
        pdf.cell(column_widths[0], row_height, rider["last_name"], border=1, align="C")
        pdf.cell(column_widths[1], row_height, rider["first_name"], border=1, align="C")
        pdf.cell(column_widths[2], row_height, str(rider["dni"]), border=1, align="C")
        pdf.cell(column_widths[3], row_height, rider["disability"], border=1, align="C")
        pdf.cell(column_widths[4], row_height, rider["insurance"], border=1, align="C")
        pdf.cell(column_widths[5], row_height, rider["tutors"], border=1, align="C")
        pdf.cell(
            column_widths[6],
            row_height,
            rider["institutional_work"],
            border=1,
            align="C",
        )
        pdf.ln()

    # Guardar el PDF en un buffer de memoria
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    # Retornar el archivo como descarga
    return send_file(
        buffer,
        as_attachment=True,
        download_name="jinetes_incompletos.pdf",
        mimetype="application/pdf",
    )
