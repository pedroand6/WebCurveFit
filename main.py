import flet as ft
import pyperclip
import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model

def main(page: ft.Page):

    page.fonts = {
        "Rubik": "/fonts/Rubik-Regular.ttf",
    }

    page.bgcolor = ft.colors.WHITE38

    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    firstCol = []
    secondCol = []

    tableRows = []

    def PasteData(e):
        tableRows.clear()
        firstCol.clear()
        secondCol.clear()
        clipboard = pyperclip.paste()
        rawData = clipboard.replace('\r', '').split("\n")

        for line in rawData:
            lineData = line.replace(",", ".").split("\t")
            try:
                firstCol.append(float(lineData[0]))
                secondCol.append(float(lineData[1]))

                tableRows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(lineData[0])),
                            ft.DataCell(ft.Text(lineData[1])),
                        ],
                ))
            except Exception as e:
                tableRows.clear()
                firstCol.clear()
                secondCol.clear()
                print(e)

        page.update()

    rows = tableRows
    
    mainContainer = ft.Container(
        bgcolor=ft.colors.LIGHT_BLUE_200,
        width=300,
        height=600,
        border_radius=10,
        padding=20,
        expand_loose=10,
        content=ft.Column([
            ft.Row([
                ft.TextField(prefix_text="f(x) = ", width=220, prefix_style=ft.TextStyle(color=ft.colors.GREY_200, size=16, weight=ft.FontWeight.BOLD), 
                         border_color=ft.colors.GREY_200, border_width=2, color=ft.colors.GREY_200, 
                         cursor_color=ft.colors.GREY_200, selection_color=ft.colors.GREY_500, hint_text="Write your equation...", 
                         hint_style=ft.TextStyle(color=ft.colors.GREY_300), text_align=ft.TextAlign.LEFT),
                ft.IconButton(icon=ft.icons.SEND, icon_color=ft.colors.GREY_200, icon_size=20, highlight_color=ft.colors.RED, hover_color=ft.colors.GREY_500)
            ]),
            ft.Container(height=5),
            ft.IconButton(icon=ft.icons.PASTE, icon_color=ft.colors.GREY_200, icon_size=20, highlight_color=ft.colors.RED, hover_color=ft.colors.GREY_500, on_click=PasteData),
            ft.ListView(expand=1, spacing=10, padding=5, controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("x", size=20, color=ft.colors.WHITE)),
                        ft.DataColumn(ft.Text("y", size=20, color=ft.colors.WHITE)),
                    ],
                    rows=rows,
                    vertical_lines=ft.BorderSide(1, "white"),
                    horizontal_lines=ft.BorderSide(1, "white"),
                    heading_row_height=40,
                    data_text_style=ft.TextStyle(color="white")
                )
            ])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    figure = plt.figure(figsize=(6, 6))

    plt.plot([1,2,3], [0, 1, 2])

    # def linearModel(x, a0, a1):
    #     return a0+a1*x

    # gmodel = Model(linearModel)  #select model      
    # params = gmodel.make_params(a0=1, a1=1) # initial params
    # result = gmodel.fit(y, params, x=X) # curve fitting
    
    plt.savefig('assets/plot.png')

    page.add(
        ft.Text("PLOT LAB", size=50, font_family="Rubik"),
        ft.Row([
            mainContainer,
            ft.Image(
                src='plot.png',
                fit=ft.ImageFit.CONTAIN,
            )
        ], width=900),
    )


ft.app(main, view=ft.AppView.WEB_BROWSER, web_renderer=ft.WebRenderer.HTML)