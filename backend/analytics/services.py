from io import BytesIO
import pandas as pd
from matplotlib import pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image


REQUIRED_COLUMNS = [
    'Session ID',
    'Rider Name',
    'Board Type',
    'Wind Speed (km/h)',
    'Wave Height (m)',
    'Speed (km/h)',
    'Duration (minutes)',
    'Distance Covered (km)',
    'Water Temperature (°C)',
]


def validate_columns(df: pd.DataFrame):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


def compute_summary(df: pd.DataFrame):
    return {
        'total_sessions': int(df.shape[0]),
        'average_wind_speed': float(df['Wind Speed (km/h)'].mean()),
        'average_rider_speed': float(df['Speed (km/h)'].mean()),
        'average_distance_covered': float(df['Distance Covered (km)'].mean()),
        'longest_session_duration': float(df['Duration (minutes)'].max()),
        'board_type_distribution': df['Board Type'].value_counts().to_dict(),
    }


def build_chart_buffers(df: pd.DataFrame):
    buffers = {}

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(df['Session ID'], df['Wind Speed (km/h)'], marker='o')
    ax.set_title('Wind Speed vs Session')
    ax.set_xlabel('Session ID')
    ax.set_ylabel('Wind Speed (km/h)')
    b1 = BytesIO()
    fig.tight_layout()
    fig.savefig(b1, format='png')
    plt.close(fig)
    b1.seek(0)
    buffers['wind_line'] = b1

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(df['Session ID'], df['Distance Covered (km)'])
    ax.set_title('Distance Covered per Session')
    ax.set_xlabel('Session ID')
    ax.set_ylabel('Distance (km)')
    b2 = BytesIO()
    fig.tight_layout()
    fig.savefig(b2, format='png')
    plt.close(fig)
    b2.seek(0)
    buffers['distance_bar'] = b2

    fig, ax = plt.subplots(figsize=(4, 4))
    board_counts = df['Board Type'].value_counts()
    ax.pie(board_counts.values, labels=board_counts.index, autopct='%1.1f%%')
    ax.set_title('Board Type Distribution')
    b3 = BytesIO()
    fig.tight_layout()
    fig.savefig(b3, format='png')
    plt.close(fig)
    b3.seek(0)
    buffers['board_pie'] = b3

    return buffers


def build_pdf_report(output_buffer: BytesIO, summary: dict, file_name: str, chart_buffers: dict):
    doc = SimpleDocTemplate(output_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph('Windsurf Performance Report', styles['Title']),
        Spacer(1, 0.2 * inch),
        Paragraph(f'Dataset: {file_name}', styles['Normal']),
        Spacer(1, 0.1 * inch),
    ]

    for key, value in summary.items():
        elements.append(Paragraph(f'<b>{key}</b>: {value}', styles['Normal']))

    elements.append(Spacer(1, 0.2 * inch))

    for chart_name in ['wind_line', 'distance_bar', 'board_pie']:
        chart = Image(chart_buffers[chart_name], width=6 * inch, height=3 * inch)
        elements.append(Paragraph(chart_name.replace('_', ' ').title(), styles['Heading3']))
        elements.append(chart)
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    output_buffer.seek(0)
