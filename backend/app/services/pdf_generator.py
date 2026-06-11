from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pdfencrypt import StandardEncryption
from io import BytesIO


def _safe(obj, attr, default='-'):
    return getattr(obj, attr, default) if obj else default


def _section_table(title, rows, col_widths):
    elements = []
    header_style = ParagraphStyle('SectionHeader', fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'), spaceAfter=4)
    elements.append(Paragraph(title, header_style))
    
    data = [["Parameter", "Code", "Value"]] + rows
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 1), (1, -1), 'Courier-Bold'),
        ('FONTSIZE', (1, 1), (1, -1), 8),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.HexColor('#2563eb')),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6*mm))
    return elements


def generate_pdf(bpan_record, password=None) -> BytesIO:
    buffer = BytesIO()
    doc_kwargs = dict(pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=10*mm, bottomMargin=10*mm)
    if password:
        doc_kwargs["encrypt"] = StandardEncryption(password, password)
    doc = SimpleDocTemplate(buffer, **doc_kwargs)
    
    elements = []
    
    # Title
    title_style = ParagraphStyle('Title', fontSize=18, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=8)
    elements.append(Paragraph("Battery Pack Aadhaar Number (BPAN)", title_style))
    
    # BPAN Code
    code_style = ParagraphStyle('Code', fontSize=16, fontName='Courier-Bold', alignment=TA_CENTER, 
                            textColor=colors.HexColor('#1e40af'), spaceAfter=6)
    elements.append(Paragraph(bpan_record.code_21char, code_style))
    
    model = bpan_record.model
    col_w = [65*mm, 25*mm, 65*mm]
    
    # BMI
    elements += _section_table("Battery Manufacturer Identifier (BMI)", [
        ["Country code", _safe(model.country, 'code'), _safe(model.country, 'name')],
        ["Manufacturer identifier", _safe(model.manufacturer, 'code'), _safe(model.manufacturer, 'name')],
    ], col_w)
    
    # BDS
    elements += _section_table("Battery Descriptor Section (BDS)", [
        ["Battery Capacity", _safe(model.capacity, 'code'), f"{_safe(model.capacity, 'value_kwh')} kWh"],
        ["Battery Chemistry", _safe(model.chemistry, 'code'), _safe(model.chemistry, 'name')],
        ["Nominal voltage", _safe(model.voltage, 'code'), f"{_safe(model.voltage, 'value_v')} V"],
        ["Cell Origin", _safe(model.cell_origin, 'code'), _safe(model.cell_origin, 'country_name')],
        ["Extinguisher Class", _safe(model.extinguisher, 'code'), _safe(model.extinguisher, 'class_name')],
    ], col_w)
    
    # BI
    elements += _section_table("Battery Identifier (BI)", [
        ["Manufacturing Year", bpan_record.year_code, str(_safe(bpan_record.year, 'year'))],
        ["Manufacturing Month", bpan_record.month_code, _safe(bpan_record.month, 'name')],
        ["Manufacturing Date", bpan_record.date_code, str(_safe(bpan_record.date, 'day_num'))],
        ["Factory Code", _safe(model.factory, 'code'), _safe(model.factory, 'factory_name')],
        ["Serial Number", str(bpan_record.serial_number).zfill(4), f"Unit {bpan_record.serial_number}"],
    ], col_w)
    
    # BMCS
    elements += _section_table("Battery Material Composition Section (BMCS)", [
        ["TAC Number", _safe(model.tac, 'code', model.tac_code), _safe(model.tac, 'tac_number', model.tac_code)],
        ["Number of cells per battery", model.num_cells_code, str(_safe(model.num_cells, 'count', model.num_cells_code))],
        ["Internal Resistance", model.internal_resistance_code, f"{_safe(model.internal_resistance, 'value_mohm', model.internal_resistance_code)} mΩ"],
        ["Battery Weight", model.weight_code, f"{_safe(model.weight, 'value_kg', model.weight_code)} kg"],
        ["Battery warranty", model.warranty_code, f"{_safe(model.warranty, 'years', model.warranty_code)} years"],
        ["Cell Type", _safe(model.cell_type, 'code'), _safe(model.cell_type, 'type_name')],
        ["Cell form Factor", model.dimensions_code, f"{_safe(model.dimensions, 'length_mm')}x{_safe(model.dimensions, 'width_mm')}x{_safe(model.dimensions, 'height_mm')} mm"],
        ["Pack Construction", _safe(model.pack_construction, 'code'), _safe(model.pack_construction, 'construction_type')],
        ["Module Construction", _safe(model.module_construction, 'code'), _safe(model.module_construction, 'construction_type')],
        ["Cooling System", _safe(model.cooling, 'code'), _safe(model.cooling, 'cooling_type')],
        ["Power at 80% SoC", model.power_80_soc_code, f"{_safe(model.power_80_soc, 'value_kw', model.power_80_soc_code)} kW"],
        ["Power at 20% SoC", _safe(model.power_20_soc, 'code', '-'), f"{model.power_20_soc_value} kW"],
    ], col_w)
    
    # BCF
    elements += _section_table("Battery Carbon Footprint (BCF)", [
        ["Total Carbon Footprint", model.carbon_footprint_code, f"{_safe(model.carbon_footprint, 'value_kgco2ekwh', model.carbon_footprint_code)} kgCO2e/kWh"],
    ], col_w)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
