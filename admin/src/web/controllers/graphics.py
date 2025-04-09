import base64
import io
from datetime import datetime
from typing import Dict, List

import matplotlib
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, send_file

from src.core.reports.graphics import (
    calculate_active_job_position_frequencies,
    calculate_diagnosis_frequencies,
    calculate_scholarship_proportion,
)
from src.web.handlers.auth import login_required, permission_required


matplotlib.use("Agg")  # Configura el backend no interactivo

bp = Blueprint("graphics", __name__, url_prefix="/graficos")


def make_pie_chart_disabilities(frequencies: Dict[str, int]) -> str:
    """
    Genera un gráfico de pastel que muestra la distribución de discapacidades.

    Parámetros:
        frequencies (Dict[str, int]): Un diccionario con las frecuencias de cada discapacidad.

    Devuelve:
        str: Una cadena base64 que representa el gráfico de pastel en formato PNG.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y")

    if not frequencies:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(
            0.5, 0.5, "No hay datos disponibles", fontsize=16, ha="center", va="center"
        )
        ax.text(
            0.5, 0.1, f"Generado: {timestamp}", fontsize=10, ha="center", va="center"
        )
        ax.axis("off")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        labels: List[str] = list(frequencies.keys())
        sizes: List[int] = list(frequencies.values())
        explode = [0.1 if i == max(sizes) else 0 for i in sizes]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontsize": 8},
            explode=explode,
            colors=plt.cm.Set2.colors,
        )
        ax.set_title(
            f"Distribución de Diagnósticos (Generado: {timestamp})", fontsize=16
        )

        for text in autotexts:
            text.set_color("white")
            text.set_fontsize(10)

        ax.legend(
            wedges,
            labels,
            title="Diagnósticos",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)

    return graph_base64


def make_scholarship_pie_chart(scholarship_counts: Dict[str, int]) -> str:
    """
    Genera un gráfico de pastel que muestra la proporción de becados vs. no becados.

    Parámetros:
        scholarship_counts (Dict[str, int]): Un diccionario con las cantidades de becados
        y no becados.

    Devuelve:
        str: Una cadena base64 que representa el gráfico de pastel en formato PNG.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y")

    if scholarship_counts["becados"] == 0 and scholarship_counts["no becados"] == 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(
            0.5, 0.5, "No hay datos disponibles", fontsize=16, ha="center", va="center"
        )
        ax.text(
            0.5, 0.1, f"Generado: {timestamp}", fontsize=10, ha="center", va="center"
        )
        ax.axis("off")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        sizes = [scholarship_counts["becados"], scholarship_counts["no becados"]]
        labels = ["Becados", "No Becados"]
        explode = [0.1, 0]
        colors = ["#6A0DAD", "#A9A9A9"]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            explode=explode,
            colors=colors,
        )
        ax.set_title(f"Proporción de Becados (Generado: {timestamp})", fontsize=16)

        for text in autotexts:
            text.set_color("white")
            text.set_fontsize(10)

        ax.legend(
            wedges,
            labels,
            title="Becados",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)

    return graph_base64


def make_bar_chart_job_positions() -> str:
    """
    Genera un gráfico de barras que muestra la distribución de puestos laborales con un timestamp.

    Devuelve:
        str: Una cadena base64 que representa el gráfico de barras en formato PNG.
    """
    position_counts = calculate_active_job_position_frequencies()
    timestamp = datetime.now().strftime("%d/%m/%Y")

    labels = list(position_counts.keys())
    counts = list(position_counts.values())
    if all(count == 0 for count in counts):
        fig = plt.figure(figsize=(8, 4))
        plt.text(
            0.5, 0.5, "No hay datos", ha="center", va="center", fontsize=16, color="red"
        )
        plt.text(
            0.5, 0.1, f"Generado: {timestamp}", fontsize=10, ha="center", va="center"
        )
        plt.axis("off")
    else:
        fig = plt.figure(figsize=(8, 4))
        bars = plt.bar(labels, counts, color="skyblue")
        plt.xlabel("Puesto Laboral")
        plt.ylabel("Cantidad de Empleados")
        plt.title(f"Distribución de Puestos Laborales (Generado: {timestamp})")
        plt.xticks(rotation=45, ha="right")

        for bar in bars:
            yval = bar.get_height() / 2
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                yval + 0.1,
                str(int(yval)),
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)

    return graph_base64


@bp.get("/discapacidades")
@login_required
@permission_required("report_show")
def show_pie_chart_disabilities() -> str:
    """
    Muestra un gráfico de pastel con la distribución de diagnósticos de discapacidades.

    Si no hay datos, se muestra un mensaje indicando que no hay datos disponibles.

    Returns:
        str: La plantilla renderizada con el gráfico en base64.
    """
    frequencies = calculate_diagnosis_frequencies()
    graph_base64 = make_pie_chart_disabilities(frequencies=frequencies)

    # Renderizar el template con el gráfico
    return render_template("graphics/disabilities_pie_chart.html", chart=graph_base64)


@bp.get("/discapacidades/download")
@login_required
@permission_required("report_show")
def download_pie_chart_disabilities() -> send_file:
    """
    Descarga el gráfico de pastel con la distribución de diagnósticos de
    discapacidades en formato PNG.

    Returns:
        send_file: El archivo de imagen PNG que contiene el gráfico.
    """
    frequencies = calculate_diagnosis_frequencies()
    # Usar la función make_pie_chart_disabilities para generar el gráfico en base64
    graph_base64 = make_pie_chart_disabilities(frequencies)

    # Decodificar el gráfico base64 y enviarlo como archivo PNG
    buf = io.BytesIO()
    buf.write(base64.b64decode(graph_base64))
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="diagnosticos_discapacidades.png",
        mimetype="image/png",
    )


@bp.get("/becados")
@login_required
@permission_required("report_show")
def show_pie_chart_scholarships() -> str:
    """
    Muestra un gráfico de pastel con la proporción de jinetes becados y no becados.

    Si no hay datos, se muestra un mensaje indicando que no hay datos disponibles.

    Returns:
        str: La plantilla renderizada con el gráfico en base64.
    """
    graph_base64 = make_scholarship_pie_chart(
        scholarship_counts=calculate_scholarship_proportion()
    )

    # Renderizar el template con el gráfico
    return render_template("graphics/scholarship_pie_chart.html", chart=graph_base64)


@bp.get("/becados/download")
@login_required
@permission_required("report_show")
def download_pie_chart_scholarships() -> send_file:
    """
    Descarga el gráfico de pastel con la proporción de jinetes becados y no becados en formato PNG.

    Returns:
        send_file: El archivo de imagen PNG que contiene el gráfico.
    """
    graph_base64 = make_scholarship_pie_chart(
        scholarship_counts=calculate_scholarship_proportion()
    )

    # Decodificar el gráfico base64 y enviarlo como archivo PNG
    buf = io.BytesIO()
    buf.write(base64.b64decode(graph_base64))
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="jinetes_amazonas_becados.png",
        mimetype="image/png",
    )


@bp.get("/empleados_por_posicion_laboral")
@login_required
@permission_required("report_show")
def show_bar_chart_job_position():
    """
    Muestra un gráfico de barras con la cantidad de empleados por posición laboral.

    Esta función genera un gráfico de barras que muestra la distribución de los empleados
    según su posición laboral. El gráfico es enviado a la plantilla HTML para ser visualizado.

    Requiere que el usuario esté autenticado y tenga el permiso 'report_show'.

    Retorna:
        render_template: La plantilla HTML con el gráfico de barras generado.
    """
    graph_base64 = make_bar_chart_job_positions()

    return render_template("graphics/job_positions_bar_chart.html", chart=graph_base64)


@bp.get("/empleados_por_posicion_laboral/download")
@login_required
@permission_required("report_show")
def download_bar_chart_job_positions():
    """
    Descarga el gráfico de barras con la cantidad de empleados por posición laboral.

    Esta función genera el gráfico de barras, lo decodifica desde base64, y lo envía como un
    archivo PNG que el usuario puede descargar.

    Requiere que el usuario esté autenticado y tenga el permiso 'report_show'.

    Retorna:
        send_file: El archivo PNG del gráfico de barras para ser descargado.
    """
    graph_base64 = make_bar_chart_job_positions()
    # Decodificar el gráfico base64 y enviarlo como archivo PNG
    buf = io.BytesIO()
    buf.write(base64.b64decode(graph_base64))
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="empleados_activos_por_posicion_laboral.png",
        mimetype="image/png",
    )
