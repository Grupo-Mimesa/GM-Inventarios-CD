from PySide6.QtCore import Qt, QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect
from PySide6.QtGui import QColor, QPixmap, QGuiApplication
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
                               QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QScrollArea,
                               QFrame, QHeaderView, QDialog, QTextEdit, QLineEdit, QMessageBox, QScrollBar)
import pandas as pd
import math
import os
import sys
from datetime import datetime


def get_image():
    path = os.path.join(get_base_path(), "assets/GM Logo-2.png")
    return path


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Cargar Archivo: Reposición de Inventarios de CD Grupo Mimesa")
        self.setFixedSize(600, 462)
        self.setStyleSheet("background-color: #003c72;")
        # Layout principal
        self.layout = QVBoxLayout()
        # Centrar el título
        self.label_titulo = QLabel(
            "Control de Inventario de Centros de Distribucion Grupo Mimesa")
        self.label_titulo.setStyleSheet(
            "color: white; font: 12pt Arial; font-weight: bold;")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_titulo)
        # Centrar el status label
        self.status_label = QLabel("No se ha seleccionado ningún archivo.")
        self.status_label.setStyleSheet("color: white; font: 12pt Arial;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)
        # Centrar el botón de seleccionar archivo
        self.button_select_file = QPushButton("Seleccionar archivo")
        self.button_select_file.setStyleSheet(
            "background-color: #94cc1c; color: white; font: 12pt Arial; padding: 4px 10px;")
        self.button_select_file.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.button_select_file,
                              alignment=Qt.AlignCenter)
        # Centrar el botón de listo
        self.button1 = QPushButton("Listo")
        self.button1.setStyleSheet(
            "background-color: #94cc1c; color: white; font: 14pt Arial; font-weight: bold;")
        self.button1.setFixedSize(92, 36)
        self.button1.clicked.connect(self.open_second_window)
        self.layout.addWidget(self.button1, alignment=Qt.AlignCenter)
        # Crear imagen logo
        self.contenedor_imagen = QWidget()
        self.contenedor_imagen.setGeometry(150, 200, 50, 50)
        path = get_image()
        self.pixmap = QPixmap()
        self.pixmap.load(path)
        self.imagen = QLabel()
        self.imagen.setPixmap(self.pixmap)
        resized_pixmap = self.pixmap.scaled(
            150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imagen = QLabel(self.contenedor_imagen)
        imagen.setPixmap(resized_pixmap)
        imagen.move(500, 500)
        self.layout.addWidget(imagen)
        self.setLayout(self.layout)
        self.file_path = None

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", "Archivos de Excel (*.xls *.xlsx)")
        if file_path:
            self.file_path = file_path
            file_name = os.path.basename(self.file_path)
            self.status_label.setText(f"Archivo seleccionado: {file_name}")

    def open_second_window(self):
        if not self.file_path:
            self.show_warning("¡Por favor, selecciona un archivo primero!")
            return

        self.second_window = SecondWindow(self.file_path)
        self.second_window.show()

    def show_warning(self, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Advertencia")
        msg_box.setText(message)
        msg_box.exec()


class SecondWindow(QWidget, QApplication):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Reposición de Inventarios de CD Grupo Mimesa")
        # SI SE QUIERE CAMBIAR LA CANTIDAD DE PALETAS POR DEFECTO CAMBIAR AQUI, POR DEFECTO 30
        self.cantidad_de_paletas_a_enviar = 30
        self.iteraciones = 0
        self.historial_iteraciones = []
        width, height = self.screens()[0].size().toTuple()
        height = height-70
        self.setFixedSize(width, height)  # (1200, 600)
        self.move(0, 0)
        self.setStyleSheet("background-color: #003c72;")
        self.tm_estandar = 30
        self.tm_adicional = 0
        self.file_path = file_path
        # Crear el QFrame imagen logo
        self.tree_frame = QFrame(self)
        self.tree_frame.setStyleSheet("background-color: #003c72;")
        self.tree_frame.setGeometry(0, 0, width, height)
        path = get_image()
        self.pixmap = QPixmap()
        self.pixmap.load(path)
        self.imagen = QLabel(self.tree_frame)
        resized_pixmap = self.pixmap.scaled(
            180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.imagen.setPixmap(resized_pixmap)
        self.imagen.move(width-180-8, 0)  # (1100, 25)

        self.set_dataframe()

        if 'Localidad' not in self.df.columns or 'Categoria' not in self.df.columns:
            return
        self.localidades_unicas = self.df['Localidad'].unique().tolist()
        self.categorias_unicas = self.df['Categoria'].unique().tolist()

        # Localidad ComboBox
        self.label_localidad = QLabel("Localidad", self.tree_frame)
        self.label_localidad.setStyleSheet(
            "color: white; font-family: Arial; font-size: 13pt; font-weight: bold;")
        self.label_localidad.move(25, 25)
        self.localidades_combobox = QComboBox(self.tree_frame)
        self.localidades_combobox.addItems(self.localidades_unicas)
        self.localidades_combobox.setStyleSheet("""
            QComboBox {
                background-color: #94cc1c;
                border: 1px solid #ccc;
                padding: 5px;
                margin: 10px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;               
            }
            QComboBox:hover {
                background-color: #a3de20;
            }
            QComboBox QAbstractItemView {
                background-color: #1c3c6b;
                border: 1px solid #ccc;
                padding: 5px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                selection-background-color: #94cc1c;
            }
            QComboBox::drop-down {
                width: 20px;
                border: 1px solid #1c3c6b;
                background-color: #1c3c6b;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #94cc1c;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #94cc1c;
                color: white;
                padding: 1px 5px;
                border: none;
            }
        """)
        self.localidades_combobox.setFixedSize(
            160, 50)  # Fijar tamaño del ComboBox
        self.localidades_combobox.move(15, 45)
        self.localidades_combobox.currentIndexChanged.connect(
            self.update_table)

        # Ordenar por ComboBox
        self.label_OrdenarPor = QLabel("Ordenar por", self.tree_frame)
        self.label_OrdenarPor.setStyleSheet(
            "color: white; font-family: Arial; font-size: 13pt; font-weight: bold;")
        self.label_OrdenarPor.move(204, 27)
        self.OrdenarPor_combobox = QComboBox(self.tree_frame)
        self.OrdenarPor_combobox.addItems(["", "Código + Descripción del producto a despachar", "Inv en Origen TM", "Inv en Destino TM", "Planificado TM", "Tránsito TM",
                                           "% Target Original", "Target de Inventario", "Paletas Sugeridas", "Nuevo % Simulado", "Corr. Paletas", "Inv Final Simulado", "% Con Corrección"])
        self.OrdenarPor_combobox.setStyleSheet("""
            QComboBox {
                background-color: #94cc1c;
                border: 1px solid #ccc;
                padding: 5px;
                margin: 10px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;               
            }
            QComboBox:hover {
                background-color: #a3de20;
            }
            QComboBox QAbstractItemView {
                background-color: #1c3c6b;
                border: 1px solid #ccc;
                padding: 5px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                selection-background-color: #94cc1c;
            }
            QComboBox::drop-down {
                width: 20px;
                border: 1px solid #1c3c6b;
                background-color: #1c3c6b;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #94cc1c;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #94cc1c;
                color: white;
                padding: 1px 5px;
                border: none;
            }
        """)
        self.OrdenarPor_combobox.setFixedSize(200, 50)
        self.OrdenarPor_combobox.move(192, 45)
        self.OrdenarPor_combobox.currentIndexChanged.connect(self.update_table)

        # Categoria ComboBox
        self.label_categoria = QLabel("Categoría", self.tree_frame)
        self.label_categoria.setStyleSheet(
            "color: white; font-family: Arial; font-size: 13pt; font-weight: bold;")
        self.label_categoria.move(25, 107)
        self.categorias_combobox = QComboBox(self.tree_frame)
        self.categorias_combobox.addItems(["TODAS"] + self.categorias_unicas)
        self.categorias_combobox.setStyleSheet("""
            QComboBox {
                background-color: #94cc1c;
                border: 1px solid #ccc;
                padding: 5px;
                margin: 10px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;               
            }
            QComboBox:hover {
                background-color: #a3de20;
            }
            QComboBox QAbstractItemView {
                background-color: #1c3c6b;
                border: 1px solid #ccc;
                padding: 5px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                selection-background-color: #94cc1c;
            }
            QComboBox::drop-down {
                width: 20px;
                border: 1px solid #1c3c6b;
                background-color: #1c3c6b;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #94cc1c;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #94cc1c;
                color: white;
                padding: 1px 5px;
                border: none;
            }
        """)
        self.categorias_combobox.setFixedSize(160, 50)
        self.categorias_combobox.move(15, 125)
        self.categorias_combobox.currentIndexChanged.connect(self.update_table)

        # label Nivel
        self.label_Nivel = QLabel("Nivel", self.tree_frame)
        self.label_Nivel.setStyleSheet(
            "color: white; font-family: Arial; font-size: 13pt; font-weight: bold;")
        self.label_Nivel.move(204, 107)
        self.Nivel_combobox = QComboBox(self.tree_frame)
        self.Nivel_combobox.addItems(["", "Mayor", "Menor"])
        self.Nivel_combobox.setStyleSheet("""
            QComboBox {
                background-color: #94cc1c;
                border: 1px solid #ccc;
                padding: 5px;
                margin: 10px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;               
            }
            QComboBox:hover {
                background-color: #a3de20;
            }
            QComboBox QAbstractItemView {
                background-color: #1c3c6b;
                border: 1px solid #ccc;
                padding: 5px;
                color: white;
                font-family: Arial;
                font-size: 14px;
                selection-background-color: #94cc1c;
            }
            QComboBox::drop-down {
                width: 20px;
                border: 1px solid #1c3c6b;
                background-color: #1c3c6b;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #94cc1c;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #94cc1c;
                color: white;
                padding: 1px 5px;
                border: none;
            }
        """)
        self.Nivel_combobox.setFixedSize(200, 50)  # Fijar tamaño del ComboBox
        self.Nivel_combobox.move(192, 125)
        self.Nivel_combobox.currentIndexChanged.connect(self.update_table)

        # Generar SJ Botón dentro del QFrame
        self.save_sj_button = QPushButton(
            "Generar Propuesta de SJ", self.tree_frame)
        self.save_sj_button.setStyleSheet(
            "background-color: #94cc1c; color: white; font: 14pt Arial; font-weight: bold;")
        self.save_sj_button.setFixedSize(250, 54)
        self.save_sj_button.move(width/2-125, 113)
        self.save_sj_button.clicked.connect(self.save_sj)

        # Iteraciones Label
        self.label_iteraciones = QLabel(
            f"Iteraciones: {self.iteraciones}", self.tree_frame)
        self.label_iteraciones.setStyleSheet(
            "color: white; font-family: Arial; font-size: 14pt; font-weight: bold; text-align: right;")
        self.label_iteraciones.move(width - 150, 100)

        # Reiniciar proceso Botón dentro del QFrame
        self.reset_table_button = QPushButton("Reiniciar", self.tree_frame)
        self.reset_table_button.setStyleSheet(
            "background-color: #94cc1c; color: white; font-family: Arial; font-size: 13pt;")
        self.reset_table_button.setFixedSize(100, 40)
        self.reset_table_button.move(width - 100 - 25, 127)
        self.reset_table_button.clicked.connect(self.reset_table)

        # Definir La tabla
        self.table = QTableWidget(self.tree_frame)
        self.table.setStyleSheet("background-color: white;")
        self.table.setGeometry(10, 188, width-20, height-210)

        # Definir label Resumen
        self.label_resumen = QLabel(f"", self.tree_frame)  # Resumen
        self.label_resumen.setStyleSheet("color: white; font: 14pt Arial;")
        self.label_resumen.move(650, 84)  # (730, 25)
        self.label_resumen.adjustSize()

        # Definir TextField Resumen
        """self.resumen = QTextEdit(self.tree_frame)
        self.resumen.setStyleSheet(
            "color: black; font: 14pt Arial; background-color: white;")
        self.resumen.setGeometry(650, 55, 250, 100)"""

        # Definir label paletas
        self.label_paletas = QLabel("Cantidad de Paletas", self.tree_frame)
        self.label_paletas.setStyleSheet(
            "color: white; font-family: Arial; font-size: 13pt; font-weight: bold;")
        self.label_paletas.move(417, 27)

        # Definir TextFiel de paletas
        self.paletas_textfield = QLineEdit(self.tree_frame)
        self.paletas_textfield.setText(str(self.cantidad_de_paletas_a_enviar))
        self.paletas_textfield.setStyleSheet(
            "color: black; font: 14pt Arial; background-color: white; text-align:center;")
        self.paletas_textfield.setGeometry(415, 53, 100, 35)
        self.paletas_textfield.textChanged.connect(self.update_table)

        # Rellenar tabla con las columnas
        self.columns_to_display = [col for col in self.df.columns if col not in [
            '%Target Inv', '%Target Inv + Trans']]
        self.table.setColumnCount(len(self.columns_to_display))
        self.table.setHorizontalHeaderLabels(self.columns_to_display)
        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.cellChanged.connect(self.manual_adjustment)

        # LLamar la funcion que calcula todo
        self.update_table()

    def set_dataframe(self):
        # Cargar el archivo Excel
        self.original_df = pd.read_excel(self.file_path, skiprows=2)
        self.df = self.original_df.copy()

        # Definir las nuevas columnas
        self.new_columns = [
            'Branchplant Origen', 'Branchplant Destino', 'Localidad', 'Categoria', 'FAMILIA 3',
            'Código + Descripción del producto a despachar', 'UOM Prim', 'Factor TM/PL', 'Factor Prim/PL',
            'Inv en Origen TM', 'Target en Origen', '%Target Origen',
            'Inv en Destino TM', 'Planificado TM', 'Tránsito TM', 'Target de Inventario',
            '% Target Original'
        ]

        # Renombrar las columnas existentes para que coincidan con las nuevas
        self.df.rename(columns={
            "'BranchPlant'[Localidad]": 'Localidad',
            'Max of Factor PL - TM': 'Factor TM/PL',
            'Max of Factor PL - Prim': 'Factor Prim/PL',
            '%Target Inv + Trans + Plan (Python)': '% Target Original',
            'Inv Exist TM': 'Inv en Destino TM',
            'Cod + Descr': 'Código + Descripción del producto a despachar'
        }, inplace=True)

        # Reordenar las columnas según el nuevo formato
        self.df = self.df[self.new_columns]
        self.df = self.df[~self.df['% Target Original'].isna()]
        self.df = self.df[~self.df['Target de Inventario'].isna()]
        self.df = self.df.fillna(0)

        # Asegurarse de que las columnas existan en el DataFrame, si no, agregarlas
        for col in ['Código + Descripción del producto a despachar duplicado 1', 'Inv en Origen TM dupli', "Inv Final en Origen TM", '%Target Final en Origen', 'Paletas Sugeridas', 'Nuevo % Simulado',
                    'Corr. Paletas', 'Inv Final Simulado', '% Con Corrección', 'TM Con Corrección',
                    'Código + Descripción del producto a despachar duplicado 2',
                    '% Target Original dupli', '% Con Corrección dupli']:
            if col not in self.df.columns:
                # Si no existe, la columna se agrega con valor 0
                self.df[col] = 0

        # Cambiar el dtype de las columnas específicas a float
        columns_to_float = ['Inv Final Simulado',
                            '% Con Corrección', 'TM Con Corrección', '% Con Corrección dupli']
        self.df[columns_to_float] = self.df[columns_to_float].astype(float)

        # Redondear a 5 decimales las columnas numéricas específicas
        columns_to_round = ['Inv en Origen TM', 'Target de Inventario',
                            'Inv en Origen TM dupli', 'Inv en Destino TM', 'Planificado TM', 'Tránsito TM']
        self.df[columns_to_round] = self.df[columns_to_round].round(5)

    def get_filtered_df(self):
        selected_localidad = self.localidades_combobox.currentText()
        selected_categoria = self.categorias_combobox.currentText()

        filtered_df = self.df.copy()

        if selected_localidad:
            filtered_df = filtered_df[filtered_df['Localidad']
                                      == selected_localidad]

        if selected_categoria and selected_categoria != "TODAS":
            filtered_df = filtered_df[filtered_df['Categoria']
                                      == selected_categoria]

        return filtered_df

    def update_table(self):

        ordenar_por = self.OrdenarPor_combobox.currentText()
        nivel = self.Nivel_combobox.currentText()

        filtered_df = self.get_filtered_df()

        # Se duplican los valores de algunas colunmas como los duplicados o % nuevo simulado con Targer original
        # Para poder hacer la primera iteracion
        filtered_df['Nuevo % Simulado'] = filtered_df['% Target Original']
        filtered_df['Código + Descripción del producto a despachar duplicado 1'] = filtered_df['Código + Descripción del producto a despachar']
        filtered_df['Código + Descripción del producto a despachar duplicado 2'] = filtered_df['Código + Descripción del producto a despachar']
        filtered_df['% Target Original dupli'] = filtered_df['% Target Original']
        filtered_df['Inv en Origen TM dupli'] = filtered_df['Inv en Origen TM']
        filtered_df['Inv Final en Origen TM'] = filtered_df['Inv en Origen TM']
        filtered_df['%Target Final en Origen'] = filtered_df['%Target Origen']

        # Palabra de control para el ciclo
        paletas_agregadas = 0
        # Lista de pedidos que no pueden despacharle nada por falta de inventario
        procesados = set()
        # Duplicado de la tabla menos las filas que no se pueden despachar por falta d inventario
        df_no_procesados = filtered_df.drop(procesados)
        # Ciclo infito hasta que paletas_agregadas sea igual a lo seleccionado en el TextField de cuantas palabras
        # Se quieren Agregar
        while paletas_agregadas < int(self.paletas_textfield.text()):
            if filtered_df.empty:
                break

            # Filtrar las filas ya procesadas
            if df_no_procesados.empty:
                break

            # Se toma la fila con menor Nuevo % Simulado
            min_value_row_idx = df_no_procesados['Nuevo % Simulado'].idxmin()
            if min_value_row_idx is None:
                break

            # Se extren datos necesitarios para la validacion, factor de pl a tm, inv en origen,target
            factor_tm_pl = float(
                df_no_procesados.at[min_value_row_idx, 'Factor TM/PL'])
            inv_en_origen_tm = float(
                df_no_procesados.at[min_value_row_idx, 'Inv Final en Origen TM'])
            target = float(
                df_no_procesados.at[min_value_row_idx, 'Target de Inventario'])

            # 1r Condición de la validación Si factor de pl a tm es menor a origen tm
            # 2r Condición que inv en origen no se 0 o menor a 0
            # 3r que target sea diferente de 0
            if factor_tm_pl <= inv_en_origen_tm and inv_en_origen_tm > 0 and target != 0:
                filtered_df.at[min_value_row_idx, 'Paletas Sugeridas'] += 1
                # Si todas las condiciones se cumple se agrega 1 paleta
                paletas_agregadas += 1
            else:
                procesados.add(min_value_row_idx)

            # Realizar los cálculos para todas las filas
            for idx, row in filtered_df.iterrows():
                # Se sacan los datos de la tabla
                transit_tm = float(row['Tránsito TM'])
                planned_tm = float(row['Planificado TM'])
                inv_exist_tm = float(row['Inv en Destino TM'])
                target_inv = float(row['Target de Inventario'])
                paletas_inv = float(row['Paletas Sugeridas'])
                Factor_Conversion = float(row["Factor TM/PL"])
                origen = float(row["Inv en Origen TM"])
                target_origen = float(row["Target en Origen"])

                try:
                    # Se calcula TargetOriginal
                    TargetOriginal = (
                        (transit_tm + planned_tm + inv_exist_tm) / target_inv) * 100

                    Paleta_a_Tm = Factor_Conversion * paletas_inv
                    # Nuevo Porcentaje %
                    nuevo_percent = (
                        (transit_tm + planned_tm + inv_exist_tm + Paleta_a_Tm) / target_inv) * 100
                    invfinal = Paleta_a_Tm + inv_exist_tm + transit_tm + planned_tm
                    # Se actualiza los nuevos valores
                    filtered_df.at[idx, 'Nuevo % Simulado'] = nuevo_percent
                    filtered_df.at[idx, 'Inv Final Simulado'] = invfinal
                    filtered_df.at[idx, '% Con Corrección'] = nuevo_percent
                    filtered_df.at[idx, 'TM Con Corrección'] = Paleta_a_Tm
                    filtered_df.at[idx,
                                   '% Con Corrección dupli'] = nuevo_percent
                    filtered_df.at[idx, '% Target Original'] = TargetOriginal
                    filtered_df.at[idx, 'Inv Final en Origen TM'] = round(
                        origen-Paleta_a_Tm, 5)
                    filtered_df.at[idx, '%Target Final en Origen'] = round(
                        origen-Paleta_a_Tm, 5)/target_origen * 100
                    filtered_df.at[idx,
                                   '% Target Original dupli'] = TargetOriginal
                except:
                    pass

                # Se vuelve a hacer la copia de la tabla con las filas que no cumplen eliminadas
                df_no_procesados = filtered_df.drop(procesados)

        # Se aplican los filtros
        if ordenar_por and nivel:
            ascending = True if nivel == "Menor" else False
            filtered_df = filtered_df.sort_values(
                by=ordenar_por, ascending=ascending)
        # Se parsea y se la agrega a los campos necesario el %
        self.table.setRowCount(filtered_df.shape[0])
        for row_idx, (_, row) in enumerate(filtered_df.iterrows()):
            try:
                target_final_origen = round(
                    float(row['%Target Final en Origen']), 5)
                con_correccion = round(
                    float(row['% Con Corrección']), 5)
                sugeridas = float(row['Paletas Sugeridas'])
                corregidas = float(row['Corr. Paletas'])

                fila_roja = (
                    target_final_origen < con_correccion and sugeridas + corregidas > 0
                )
            except:
                fila_roja = False

            for col_idx, col in enumerate(self.columns_to_display):
                value = row[col]
                if col in ['Inv Final Simulado']:
                    value = round(value, 5)
                if col in ['%Target Final en Origen', 'Nuevo % Simulado', '% Con Corrección', '% Con Corrección dupli', '% Target Original', '% Target Original dupli']:
                    value = round(float(value), 5)
                    value = f"{value:.2f}%"

                # Se carga en la tabla y se colorea
                item = QTableWidgetItem(str(value))

                if fila_roja:
                    color_base = QColor(255, 150, 150)  # Rojo claro
                else:
                    if col_idx in range(17):  # Gris
                        color_base = QColor(169, 169, 169)  # Gris
                    elif col_idx in range(17, 27):  # Azul
                        color_base = QColor(173, 216, 230)  # Azul claro
                    elif col_idx in range(27, 30):  # Verde
                        color_base = QColor(144, 238, 144)  # Verde claro
                    else:
                        color_base = QColor(255, 255, 255)  # Blanco

                item.setBackground(color_base)
                self.table.setItem(row_idx, col_idx, item)

        self.tm_adicional = 0
        self.label_resumen.setText(
            f"Total paletas a enviar: {paletas_agregadas}")
        self.label_resumen.adjustSize()

        # Bloquear edición en todas las columnas excepto la columna 23
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if col != 23:  # Bloquear edición en todas las columnas excepto la columna 23
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.label_iteraciones.setText(f"Iteraciones: {self.iteraciones}")

        self.current_df = filtered_df.copy()

    def manual_adjustment(self, row, column):

        if (column == 23):

            column_names = [self.table.horizontalHeaderItem(
                i).text().lower() for i in range(self.table.columnCount())]

            factorTMPL_index = column_names.index('factor tm/pl')
            invOrigen_index = column_names.index('inv en origen tm')
            targetOrigen_index = column_names.index('target en origen')
            invDestino_index = column_names.index('inv en destino tm')
            planificado_index = column_names.index('planificado tm')
            transito_index = column_names.index('tránsito tm')
            targetInv_index = column_names.index('target de inventario')
            invFinalOrigen_index = column_names.index('inv final en origen tm')
            porcentajeTargetFinalOrigen_index = column_names.index(
                '%target final en origen')
            sugeridas_index = column_names.index('paletas sugeridas')
            corregidas_index = column_names.index('corr. paletas')
            invFinalSimulado_index = column_names.index('inv final simulado')
            porcentajeCorregido_index = column_names.index('% con corrección')
            tmCorregido_index = column_names.index('tm con corrección')
            porcentajeCorregido2_index = column_names.index(
                '% con corrección dupli')

            transit_tm = float(self.table.item(row, transito_index).text())
            planned_tm = float(self.table.item(row, planificado_index).text())
            inv_exist_tm = float(self.table.item(row, invDestino_index).text())
            target_inv = float(self.table.item(row, targetInv_index).text())
            paletas_inv = float(self.table.item(row, sugeridas_index).text())
            paletas_Agregada = float(
                self.table.item(row, corregidas_index).text())
            Factor_Conversion = float(
                self.table.item(row, factorTMPL_index).text())
            origen = float(self.table.item(row, invOrigen_index).text())
            target_origen = float(self.table.item(
                row, targetOrigen_index).text())

            Paleta_A_TM = Factor_Conversion*(paletas_Agregada+paletas_inv)

            origenfinal = round(origen-Paleta_A_TM, 5)
            item_origenfinal = QTableWidgetItem(str(origenfinal))
            self.table.setItem(row, invFinalOrigen_index, item_origenfinal)

            targetFinalOrigen = round(origenfinal/target_origen*100, 2)
            item_targetFinalOrigen = QTableWidgetItem(
                f"{targetFinalOrigen:.2f}%")
            self.table.setItem(
                row, porcentajeTargetFinalOrigen_index, item_targetFinalOrigen)

            inv_final2 = round(Paleta_A_TM+transit_tm +
                               planned_tm+inv_exist_tm, 2)
            item_inv_final2 = QTableWidgetItem(str(inv_final2))
            self.table.setItem(row, invFinalSimulado_index, item_inv_final2)

            porcCorregido = ((transit_tm + planned_tm + inv_exist_tm +
                              Paleta_A_TM) / target_inv) * 100
            porcCorregido = round(porcCorregido, 2)
            porcCorregido = f"{porcCorregido:.2f}%"
            item_porcCorregido = QTableWidgetItem(porcCorregido)
            self.table.setItem(
                row, porcentajeCorregido_index, item_porcCorregido)

            item_tmCorregido = QTableWidgetItem(str(Paleta_A_TM))
            self.table.setItem(row, tmCorregido_index, item_tmCorregido)

            item_porcCorregido2 = QTableWidgetItem(porcCorregido)
            self.table.setItem(
                row, porcentajeCorregido2_index, item_porcCorregido2)

            self.set_row_color(row)

            self.suma_total = 0
            for fila in range(self.table.rowCount()):
                item = self.table.item(fila, corregidas_index)
                if item is not None:
                    self.suma_total += float(item.text())
            self.label_resumen.setText(f"Total paletas a enviar: {
                                       self.tm_estandar+self.suma_total}")
            self.label_resumen.adjustSize()
        else:
            pass

    def set_row_color(self, row):

        try:
            column_names = [
                self.table.horizontalHeaderItem(i).text().lower()
                for i in range(self.table.columnCount())
            ]

            porcentaje_target_index = column_names.index(
                '%target final en origen')
            porcentaje_corregido_index = column_names.index('% con corrección')
            sugeridas_index = column_names.index('paletas sugeridas')
            corregidas_index = column_names.index('corr. paletas')

            target_final_origen = float(
                self.table.item(row, porcentaje_target_index)
                .text()
                .replace('%', '')
            )
            con_correccion = float(
                self.table.item(row, porcentaje_corregido_index)
                .text()
                .replace('%', '')
            )

            sugeridas = float(self.table.item(row, sugeridas_index).text())
            corregidas = float(self.table.item(row, corregidas_index).text())

            fila_roja = (
                target_final_origen < con_correccion and
                sugeridas + corregidas > 0
            )

        except:
            fila_roja = False

        for col in range(self.table.columnCount()):

            item = self.table.item(row, col)

            if item is None:
                continue

            if fila_roja:
                item.setBackground(QColor(255, 150, 150))
            else:
                # Colores originales
                if col in range(17):
                    item.setBackground(QColor(169, 169, 169))
                elif col in range(17, 27):
                    item.setBackground(QColor(173, 216, 230))
                elif col in range(27, 30):
                    item.setBackground(QColor(144, 238, 144))
                else:
                    item.setBackground(QColor(255, 255, 255))

    def save_sj(self):
        try:
            selected_localidad = self.localidades_combobox.currentText().lower()
            selected_categoria = self.categorias_combobox.currentText().lower()

            if not selected_localidad or not selected_categoria:
                self.show_message(
                    "Error", "Debe seleccionar una localidad y una categoría.", tipo='error')
                return

            column_names = [self.table.horizontalHeaderItem(
                i).text().lower() for i in range(self.table.columnCount())]

            if 'localidad' not in column_names or 'categoria' not in column_names:
                self.show_message(
                    "Error", "Las columnas 'localidad' y 'categoria' no están presentes en la tabla.", tipo='error')
                return

            localidad_index = column_names.index('localidad')
            categoria_index = column_names.index('categoria')
            codDescr_index = column_names.index(
                'código + descripción del producto a despachar')
            factorTMPL_index = column_names.index('factor tm/pl')
            factorPrimPL_index = column_names.index('factor prim/pl')
            invFinalOrigen_index = column_names.index('inv final en origen tm')
            tm_index = column_names.index('paletas sugeridas')
            corr_index = column_names.index('corr. paletas')

            filtered_data = []
            for row in range(self.table.rowCount()):
                item_localidad = self.table.item(row, localidad_index)
                item_categoria = self.table.item(row, categoria_index)
                item_tm = self.table.item(row, tm_index)
                item_corr = self.table.item(row, corr_index)

                if item_localidad and item_categoria and item_tm:
                    localidad_match = selected_localidad in item_localidad.text().lower()
                    categoria_match = selected_categoria in item_categoria.text(
                    ).lower() or selected_categoria == "todas"

                    tm_value = float(item_tm.text()) if item_tm else 0
                    corr_value = float(item_corr.text()) if item_corr else 0
                    tm_final = tm_value + corr_value

                    if localidad_match and categoria_match and tm_final != 0:
                        self.table.setRowHidden(row, False)
                        row_data = []
                        for col in [5, 16, 6, 0, 1]:
                            item = self.table.item(row, col)
                            if item:
                                text = item.text()
                                if col == 5:
                                    text = text.split(' ')[0]
                                elif col == 16:
                                    item_Sugeridas = self.table.item(
                                        row, tm_index)
                                    item_FactorPrim = self.table.item(
                                        row, factorPrimPL_index)
                                    item_Corregidas = self.table.item(
                                        row, corr_index)
                                    if item_Corregidas and item_FactorPrim:
                                        valor = (
                                            float(item_Sugeridas.text()) + float(item_Corregidas.text()))
                                        valor2 = int(
                                            valor * float(item_FactorPrim.text()))
                                        valor3 = round(valor2, 2)
                                        text = str(valor3)
                                    else:
                                        text = '0'
                                elif col in [0, 1]:
                                    text = "0"+text
                                row_data.append(text)
                            else:
                                row_data.append('')
                        row_data.insert(2, '1')
                        filtered_data.append(row_data)
                    else:
                        pass
                for idx, row2 in self.df.iterrows():
                    if row2['Código + Descripción del producto a despachar'] == self.table.item(row, codDescr_index).text():
                        self.df.at[idx, 'Inv en Origen TM'] = float(
                            self.table.item(row, invFinalOrigen_index).text())
                        if row2['Localidad'].lower() == selected_localidad:
                            paletas_inv = float(
                                self.table.item(row, tm_index).text())
                            paletas_Agregada = float(
                                self.table.item(row, corr_index).text())
                            Factor_Conversion = float(
                                self.table.item(row, factorTMPL_index).text())
                            Paleta_A_TM = Factor_Conversion * \
                                (paletas_Agregada+paletas_inv)
                            self.df.at[idx, 'Planificado TM'] += Paleta_A_TM

            if not filtered_data:
                self.show_message(
                    "Información", "No se encontraron datos que coincidan con los criterios seleccionados.")
                return

            columns = ['Sku', 'Cantidad', 'Precio total', 'UOM Prim',
                       'Branchplant Origen', 'Branchplant Destino']
            df = pd.DataFrame(filtered_data, columns=columns)
            timestamp = datetime.now()
            file_name = f'Subida_Sj_{selected_localidad.upper()}_{
                selected_categoria.upper()}_{timestamp.strftime('%Y%m%d%H%M%S')}.xlsx'
            script_dir = get_app_path()
            new_file_path = os.path.join(script_dir, file_name)
            columnas_a_quitar = [
                'Código + Descripción del producto a despachar duplicado 1',
                "Inv en Origen TM dupli",
                'Código + Descripción del producto a despachar duplicado 2',
                '% Target Original dupli',
                '% Con Corrección dupli'
            ]
            df_filtrado = self.current_df.copy()
            df_filtrado = df_filtrado.drop(
                columns=columnas_a_quitar, errors='ignore')

            df_iteracion = df_filtrado.copy()
            df_iteracion.insert(
                0, 'Fecha Data', self.original_df['Fecha Data'].iloc[0])
            df_iteracion.insert(1, 'Iteración', self.iteraciones + 1)
            df_iteracion.insert(2, 'Fecha Iteración',
                                pd.to_datetime(timestamp))
            self.historial_iteraciones.append(df_iteracion)

            df_final = pd.concat(self.historial_iteraciones, ignore_index=True)

            with pd.ExcelWriter(new_file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Propuesta SJ', index=False)
                df_final.to_excel(
                    writer, sheet_name='Iteraciones', index=False)

            self.show_message("Información", f"El archivo '{
                file_name}' fue creado con éxito.")
            self.iteraciones += 1
            self.update_table()
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")
            self.show_message(
                "Error", f"Se produjo un error: {e}", tipo='error')

    def reset_table(self):
        self.df = pd.read_excel(self.file_path, skiprows=2)
        self.paletas_textfield.setText(str(self.cantidad_de_paletas_a_enviar))
        self.iteraciones = 0
        self.historial_iteraciones = []
        self.set_dataframe()
        self.update_table()

    def show_message(self, titulo, mensaje, tipo='informacion'):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)

        # Aplicar estilo CSS para cambiar el color de fondo
        msg_box.setStyleSheet("QMessageBox { background-color: white; }")

        if tipo == 'informacion':
            msg_box.setIcon(QMessageBox.Information)
        elif tipo == 'error':
            msg_box.setIcon(QMessageBox.Critical)

        msg_box.exec()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

"""
formado app
0 Branchplant Origen
1 Branchplant Destino
2 Localidad
3 Categoria
4 FAMILIA 3
5 Cod + Descr
6 UOM Prim
7 Factor TM/PL
8 Factor Prim/PL
9 Inv en Origen TM
10 Target en Origen
11 %Target Origen
12 Inv en Destino TM
13 Planificado TM
14 Tránsito TM
15 Target de Inventario
16 % Target Original 
17 Cod + Descr dupli
18 Inv en Origen TM ref
19 Inv en Origen Final TM
20 % Target Final en Origen
21 Paletas Sugeridas 
22 Nuevo % Simulado 
23 Corrección de Paletas
24 Inv Final Simulado
25 % Con Corrección
26 TM Con Corrección
27 Cod + Descr dupli
28 % Target Original dupli
29 % Con Corrección dupli
"""

"""
archivo de excel original
0 Localidad
1 Categoria
2 FAMILIA 3
3 Cod + Descr
4 Branchplant Origen
5 Branchplant Destino
6 UOM Prim
7 Inv en Origen TM
8 Inv Exist TM
9 Planificado TM
10 Tránsito TM
11 Target de Inventario
12 %Target Inv + Trans + Plan (Python)
13 Max of Factor PL - TM
14 Max of Factor PL - Prim
15 Fecha Data
16 Dscr Criterio Target
17 Localidad Origen
18 Target en Origen
19 %Target Origen
"""
