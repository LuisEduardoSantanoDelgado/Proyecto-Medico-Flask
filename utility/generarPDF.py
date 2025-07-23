import unicodedata
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, Spacer, KeepTogether, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ========================
# CONFIGURACIÓN DE FUENTES
# ========================

pdfmetrics.registerFont(TTFont("Arial", "static/Fonts/ARIAL.TTF"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "static/Fonts/ARIALBD.TTF"))

NORMAL_FONT = "Arial"
BOLD_FONT = "Arial-Bold"

# ==================
# CARPETA DE DESTINO
# ==================

FOLDER_PATH = "Citas/"

# =================
# MEDIDAS GENERALES
# =================

MARGINS = 2 * cm
ELEMENT_SPACING = 2 * cm

TEXT_BOX_HEIGHT = 5 * cm
DATE_WIDTH, DATE_HEIGHT = 5 * cm, 0.5 * cm
DOCTOR_DATA_WIDTH, DOCTOR_DATA_HEIGHT = 8 * cm, 3 * cm

# ======================
# IMÁGENES Y DIMENSIONES
# ======================

CLINIC_NAME_PATH = "static/Img/Nombre_consultorio.png"
CLINIC_LOGO_PATH = "static/Img/Logo_consultorio.png"
SIGNATURE_PATH = "static/Img/Firma_doctor.png"

CLINIC_NAME_SIZE = 2 * cm
CLINIC_LOGO_SIZE = 4 * cm
BIGGEST_IMAGE = max(CLINIC_NAME_SIZE, CLINIC_LOGO_SIZE)

SIGNATURE_WIDTH = 12 * cm
SIGNATURE_HEIGHT = SIGNATURE_WIDTH / 3

# =====================
# VARIABLES COMPARTIDAS
# =====================

styles_dictionary = {}

# =========================
# CREAR NOMBRE DE DOCUMENTO
# =========================

def createFilename(patient_name, appointment_date):

    def noAccents(text):
        return ''.join(
            character for character in unicodedata.normalize('NFD', text)
            if unicodedata.category(character) != 'Mn'
        )

    split_name = patient_name.split()
    name = split_name[0]
    last_name = split_name[2] if len(split_name) > 2 else split_name[1]

    name = noAccents(name)
    last_name = noAccents(last_name)

    # Datos normalizados
    normalized_name = f"{name}_{last_name}"
    normalized_date = appointment_date.replace("/", "-")
    filename = f"{normalized_name}_{normalized_date}.pdf"

    # Regresar el nombre del archivo
    return filename

# ==========================
# CREAR PLANTILLA DE ESTILOS
# ==========================

def generateStyle(font_index, font_size, alignment_value, hex_color):
    fonts = [NORMAL_FONT, BOLD_FONT]

    style = ParagraphStyle(
        name = "generic_style",
        fontName = fonts[font_index],
        fontSize = font_size,
        leading = font_size + 2,
        alignment = alignment_value,
        textColor = colors.HexColor(hex_color)
    )

    return style

# =======================
# CREAR Y GUARDAR ESTILOS
# =======================

def setUpStyles():
    styles_dictionary["header_footer_text"] = generateStyle(0, 10, 0, "#000000")
    styles_dictionary["body_title"] = generateStyle(1, 14, 0, "#000000")
    styles_dictionary["body_text"] = generateStyle(0, 12, 0, "#000000")
    styles_dictionary["table_title"] = generateStyle(1, 14, 1, "#F2F2F2")
    styles_dictionary["table_text"] = generateStyle(0, 12, 1, "#000000")
    styles_dictionary["generic"] = generateStyle(1, 12, 1, "#000000")

class conditionalSpacer(Spacer):
    def wrap(self, aW, aH):
        if aH < self.height:
            return (0, 0)
        return super().wrap(aW, aH)

class PDFGenerator:
    def __init__(self, filename, session_data):
        self.filename = filename
        self.appointment_data = session_data
        
        document_top_margin = MARGINS + BIGGEST_IMAGE + ELEMENT_SPACING
        document_bottom_margin = MARGINS
        
        self.document = BaseDocTemplate(
            filename,
            pagesize = letter,
            leftMargin = MARGINS,
            rightMargin = MARGINS,
            topMargin = document_top_margin,
            bottomMargin = document_bottom_margin
        )

        frame_height = self.document.height
        frame = Frame(
            self.document.leftMargin,
            self.document.bottomMargin,
            self.document.width,
            frame_height,
            leftPadding = 0, rightPadding = 0,
            bottomPadding = 0, topPadding = 0
        )

        template = PageTemplate(
            id = "main",
            frames = [frame],
            onPage = self.header,
            onPageEnd = self.footer
        )

        self.document.addPageTemplates([template])
        self.story = []
        self._last_page = 1

    def header(self, canvas, document):
        canvas.saveState()

        default_y_position = self.document.pagesize[1] - BIGGEST_IMAGE - MARGINS

        # Dibujar la imagen del nombre de la clínica
        canvas.drawImage(
            CLINIC_NAME_PATH,
            x = MARGINS,
            y = default_y_position + (BIGGEST_IMAGE - CLINIC_NAME_SIZE) / 2,
            width = CLINIC_NAME_SIZE,
            height = CLINIC_NAME_SIZE,
            preserveAspectRatio = True,
            mask = "auto"
        )

        # Dibujar la imagen del logo de la clínica
        clinic_logo_x_position = self.document.pagesize[0] - MARGINS - CLINIC_LOGO_SIZE
        clinic_logo_y_position = default_y_position + (BIGGEST_IMAGE - CLINIC_LOGO_SIZE) / 2

        canvas.drawImage(
            CLINIC_LOGO_PATH,
            x = clinic_logo_x_position,
            y = clinic_logo_y_position,
            width = CLINIC_LOGO_SIZE,
            height = CLINIC_LOGO_SIZE,
            preserveAspectRatio = True,
            mask = "auto"
        )

        date_text = f"Fecha de la cita: {self.appointment_data["fecha"]}"
        date_paragraph = Paragraph(date_text, styles_dictionary["header_footer_text"])

        # Definir las coordenadas de la fecha de la cita en el encabezado
        difference = DATE_WIDTH - CLINIC_LOGO_SIZE
        date_x_position = clinic_logo_x_position - difference + DATE_HEIGHT
        date_y_position = clinic_logo_y_position - 2 * DATE_HEIGHT
        date_paragraph.wrapOn(canvas, DATE_WIDTH, DATE_HEIGHT)
        date_paragraph.drawOn(canvas, date_x_position, date_y_position)

        # Insertar datos médicos entre ambas imágenes
        doctor_data_text = f"""
        Dr@. {self.appointment_data["medico"]}<br/>
        Medicina general<br/>
        Cédula profesional: {self.appointment_data["cedula"]}<br/>
        Egresado de: UNAM<br/>
        Correo electrónico: {self.appointment_data["correo_electronico"]}<br/>
        Teléfono: +52 442 123 4567
        """
        
        doctor_data_paragraph = Paragraph(doctor_data_text, styles_dictionary["header_footer_text"])
        left = MARGINS + CLINIC_NAME_SIZE
        right = self.document.pagesize[0] - MARGINS - CLINIC_LOGO_SIZE
        remaining_space = right - left
        doctor_data_x_position = left + (remaining_space - DOCTOR_DATA_WIDTH) / 2
        doctor_data_y_position =  default_y_position + (BIGGEST_IMAGE - DOCTOR_DATA_HEIGHT) / 2
        doctor_data_paragraph.wrapOn(canvas, DOCTOR_DATA_WIDTH, DOCTOR_DATA_HEIGHT)
        doctor_data_paragraph.drawOn(canvas, doctor_data_x_position, doctor_data_y_position)

        canvas.restoreState()
    
    def body(self):
        yield self._patient_table()

        for section_title, text in [
            ("Síntomas del paciente", self.appointment_data.get("sintomas", "")),
            ("Diagnóstico", self.appointment_data.get("diagnostico", "")),
            ("Tratamiento", self.appointment_data.get("tratamiento", "")),
            ("Estudios del paciente (opcional)", "N/A" if self.appointment_data.get("estudios", "") == "" else self.appointment_data["estudios"])
        ]:
            
            title_paragraph = Paragraph(section_title, styles_dictionary["body_title"])
            text_box_format = Table([[Paragraph(text, styles_dictionary["body_text"])]],  colWidths = [self.document.width], rowHeights = [TEXT_BOX_HEIGHT])
            text_box_format.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D0D0D0")),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 0.5*cm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5*cm),
                ("LEFTPADDING", (0, 0), (-1, -1), 0.5*cm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0.5*cm)
            ]))

            yield conditionalSpacer(1, ELEMENT_SPACING)
            yield KeepTogether([title_paragraph, Spacer(1, ELEMENT_SPACING / 4), text_box_format])

        yield Spacer(1, 2 * ELEMENT_SPACING)

        signature_image = Image(SIGNATURE_PATH, width = SIGNATURE_WIDTH, height = SIGNATURE_HEIGHT)

        signature_with_line = Table(
            [[signature_image]],
            colWidths = [SIGNATURE_WIDTH],
            rowHeights = [SIGNATURE_HEIGHT]
        )

        signature_with_line.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 1, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), -SIGNATURE_HEIGHT * 0.2),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0)
        ]))

        yield signature_with_line
        yield Spacer(1, 0.2 * cm)
        yield Paragraph("Firma del médico", styles_dictionary["generic"])

    def _patient_table(self):
        available_width = self.document.pagesize[0] - 2 * MARGINS

        table_data = [
            [Paragraph("Datos del paciente", styles_dictionary["table_title"]), "", ""],
            [Paragraph("Paciente", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("paciente", ""), styles_dictionary["table_text"]), ""],
            [Paragraph("<b>Campo</b>", styles_dictionary["table_text"]), Paragraph("<b>Valor</b>", styles_dictionary["table_text"]), Paragraph("<b>Unidad de medida</b>", styles_dictionary["table_text"])],
            [Paragraph("Edad", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("edad", ""), styles_dictionary["table_text"]), Paragraph("años", styles_dictionary["table_text"])],
            [Paragraph("Peso", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("peso", ""), styles_dictionary["table_text"]), Paragraph("kg", styles_dictionary["table_text"])],
            [Paragraph("Altura", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("altura", ""), styles_dictionary["table_text"]), Paragraph("cm", styles_dictionary["table_text"])],
            [Paragraph("Temperatura", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("temperatura", ""), styles_dictionary["table_text"]), Paragraph("°C", styles_dictionary["table_text"])],
            [Paragraph("Latidos por minuto", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("latidos", ""), styles_dictionary["table_text"]), Paragraph("---", styles_dictionary["table_text"])],
            [Paragraph("Saturación de oxígeno", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("saturacion", ""), styles_dictionary["table_text"]), Paragraph("%", styles_dictionary["table_text"])],
            [Paragraph("Glucosa", styles_dictionary["body_text"]), Paragraph(self.appointment_data.get("glucosa", ""), styles_dictionary["table_text"]), Paragraph("mg/dL", styles_dictionary["table_text"])]
        ]

        table = Table(
            table_data,
            colWidths = [available_width * 0.4, available_width * 0.2, available_width * 0.4],
            rowHeights=[cm] + [0.8 * cm] * 9
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#404040")),
            ("SPAN", (0, 0), (-1, 0)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
            ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#ADADAD")),
            ("BACKGROUND", (1, 1), (-1, 1), colors.HexColor("#D9D9D9")),
            ("SPAN", (1, 1), (-1, 1)),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#808080")),
            ("TEXTCOLOR", (0, 2), (-1, 2), colors.black),
            ("BACKGROUND", (0, 3), (0, -1), colors.HexColor("#ADADAD")),
            ("BACKGROUND", (1, 3), (1, -1), colors.HexColor("#D9D9D9")),
            ("BACKGROUND", (2, 3), (2, -1), colors.HexColor("#D0D0D0")),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5)
        ]))

        return table

    def footer(self, canvas, document):
        canvas.saveState()
        footer_style = styles_dictionary["header_footer_text"]
        current_date  = datetime.now().strftime("%d/%m/%Y")

        footer_text = f"""
        Elaborado por: Sistema de administración de citas<br/>
        Aprobado por: Jesús Emmanuel Rivero Velázquez, gestor del sistema<br/>
        Fecha: {current_date}
        """

        footer_paragraph = Paragraph(footer_text, footer_style)
        footer_width = self.document.pagesize[0] - 2 * MARGINS
        footer_height = MARGINS
        footer_x_position = MARGINS
        footer_y_position = cm
        footer_paragraph.wrapOn(canvas, footer_width, footer_height)
        footer_paragraph.drawOn(canvas, footer_x_position, footer_y_position)
        canvas.restoreState()

def generateDocument(session_data):

    # Cargar los estilos del diccionario
    setUpStyles()

    patient_name, appointment_date = session_data["paciente"], session_data["fecha"]
    filename = createFilename(patient_name, appointment_date)

    generator = PDFGenerator(FOLDER_PATH + filename, session_data)
    for element in generator.body():
        generator.story.append(element)
    generator.document.build(generator.story)
    print("Documento PDF generado exitosamente")