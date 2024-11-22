import flet as ft
import pyperclip
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from numpy import sin, cos, exp, tan
from lmfit import Model
import lmfit
import re
from flet.matplotlib_chart import MatplotlibChart

mpl.use("svg")

def main(page: ft.Page):

    #Importa as fontes usadas da pasta
    page.fonts = {
        "Rubik": "/fonts/Rubik-Regular.ttf",
    }

    page.bgcolor = ft.colors.WHITE38

    #Alinhamento de todos os itens da página no centro
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    firstCol = [] #Primeira coluna de dados (x)
    secondCol = [] #Segunda coluna de dados (y)

    tableRows = []

    def PasteData(e):
        '''
        (control) -> None
        
        Função ativada ao clicar no botão para copiar e colar os dados em
        formato no estilo csv da área de transferência do usuário.
        '''
        
        #Primeiro limpamos todas as linhas e colunas dos dados
        tableRows.clear()
        firstCol.clear()
        secondCol.clear()
        clipboard = pyperclip.paste() #Pega o conteúdo da sua área de transferência como uma string
        rawData = clipboard.replace('\r', '').split("\n") #Divide a string em listas por quebra de linha e remove os \r

        #Para cada linha de dado, separa ela em duas colunas, trocando eventuais vírgulas por ponto e adiciona os dados
        #em suas colunas certas e células da tabela do flet
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

    rows = tableRows #Pega as linhas com dados atualizados
    
    #Cria um plot vazio para mostrar
    figure = plt.figure(figsize=(6, 6))
    plt.plot()
    
    def sendPlot(e):
        '''
        (control) -> None
        
        Esta função é chamada quando o botão para enviar os dados ao ajuste é
        apertado. Ela plota os dados base e a partir da função fornecida
        pelo usuário, é feito um ajuste e plotado para a exibição.
        '''
        plt.clf() #Limpa o plot
        plt.plot(firstCol, secondCol, 'o', label='data') #Plota as duas colunas de dados como scatter
        plt.legend()
        
        expr = e.control.parent.controls[0].value #Pega a string da função dada pelo usuário no TextField
        
        if expr == '': return #Se ela for nula devemos apenas plotar os dados sem ajuste
        
        #Pegamos todos os parâmetros utilizados pela função como letras ou conjuntos de letras quaisquer do alfabeto, com exceção do 'x' (a variável)
        #e outras combinações que podem ser utilizadas como funções
        paramString = list(set(re.findall(r'\b[a-zA-Z_]\w*\b', expr)) - {'x', 'np', 'cos', 'sin', 'tan', 'exp'})
        
        def make_func(expres):
            '''
            (string) -> função
            
            Função feita para obter a função equivalente à expressão anterior em string como algo executável do python
            '''
            #String que servirá como nossa função de ajuste
            funcstr=f'''def func(x, **params): 
            for key, value in params.items():
                exec(f'{{key}} = float({{value}})', globals()) #Associa e declara cada parâmetro da expressão como uma variável associada da função (**params -> um ou mais parâmetros)

            return {expres}'''
            
            exec(funcstr, globals())
            
            return func
        
        #Cria os parâmetros para o lmfit com os parâmetros anteriores
        params = lmfit.Parameters()
        for param in paramString:
            params.add(param, value=1)
        
        f = make_func(expr)
        
        gmodel = Model(f)  #Seleciona um modelo da espressão    
        result = gmodel.fit(secondCol, params, x=firstCol) # Ajusta a curva e os parâmetros
        bestFit = result.best_fist

        plt.plot(firstCol, bestFit, '-', label='fit') #Plota os resultados
        plt.legend()
        
        page.update()
    
    #Container principal, ao lado do plot do gráfico
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
                ft.IconButton(icon=ft.icons.SEND, icon_color=ft.colors.GREY_200, icon_size=20, highlight_color=ft.colors.RED, hover_color=ft.colors.GREY_500, on_click=sendPlot)
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

    page.add(
        ft.Text("PLOT LAB", size=50, font_family="Rubik"),
        ft.Row([
            mainContainer,
            MatplotlibChart(figure, expand=True)
        ], width=900),
    )


ft.app(main, view=ft.AppView.WEB_BROWSER, web_renderer=ft.WebRenderer.HTML)