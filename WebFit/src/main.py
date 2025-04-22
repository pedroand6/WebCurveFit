import flet as ft
import matplotlib.pyplot as plt
from matplotlib import use
from numpy import linspace, array
from re import findall
from flet.matplotlib_chart import MatplotlibChart
import sys

use("svg")

async def main(page: ft.Page):

    if sys.platform == "emscripten": # check if run in Pyodide environment
        import micropip
        await micropip.install("symfit")

    from symfit import parameters, variables, Fit, cos, sin, tan, exp, pi

    page.bgcolor = ft.Colors.WHITE

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
        data = page.get_clipboard()
        clipboard = array([[float(j) for j in i.split('\t')] for i in data.splitlines()]) #Pega o conteúdo da sua área de transferência como um dataframe

        #Para cada linha de dado, separa ela em duas colunas, trocando eventuais vírgulas por ponto e adiciona os dados
        #em suas colunas certas e células da tabela do flet
        for row in clipboard:
            rowdata = [float(item) for item in row]

            try:
                firstCol.append(rowdata[0])
                secondCol.append(rowdata[1])

                tableRows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(rowdata[0])),
                            ft.DataCell(ft.Text(rowdata[1])),
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
        paramString = list(set(findall(r'\b[a-zA-Z_]\w*\b', expr)) - {'x', 'np.', 'cos', 'sin', 'tan', 'exp', 'e', 'pi'})
        
        def make_func(expres):
            '''
            (string) -> função
            
            Função feita para obter a função equivalente à expressão anterior em string como algo executável do python
            '''
            paramsSeq = ''
            for i in params.keys():
                paramsSeq += f',{i}'

            #String que servirá como nossa função de ajuste
            funcstr=f'''def func(x{paramsSeq}): return {expres}'''
            
            exec(funcstr, globals())
            
            return func
        
        #Cria os parâmetros para o symfit com os parâmetros anteriores
        params = {}
        for param in paramString:
            params[param] = 0

        paramsSeq = ''
        for i in params.keys():
            paramsSeq += f'{i},'
        
        localdict = {}
        globals()['parameters'] = parameters
        exec(f'{paramsSeq[0:-1]} = parameters("{paramsSeq[0:-1]}")', globals(), localdict)
        
        x, y = variables('x, y')
        f = make_func(expr)

        localdict['cos'] = cos
        localdict['sin'] = sin
        localdict['tan'] = tan
        localdict['exp'] = exp
        localdict['e'] = exp
        localdict['pi'] = pi

        exec(f'model = {{ y: {expr} }}', {'x':x, 'y':y} | localdict, localdict)
        model = localdict['model']
           
        fit = Fit(model, firstCol, secondCol) # Ajusta a curva e os parâmetros
        fit_result = fit.execute()

        x_data = linspace(min(firstCol), max(firstCol), 100)

        plt.plot(firstCol, secondCol, 'o')
        plt.plot(x_data, fit.model(x=x_data, **fit_result.params).y, '-', label='fit') #Plota os resultados
        plt.legend()
        
        page.update()
    
    #Container principal, ao lado do plot do gráfico
    mainContainer = ft.Container(
        bgcolor=ft.Colors.LIGHT_BLUE_200,
        width=300,
        height=600,
        border_radius=10,
        padding=20,
        expand_loose=10,
        content=ft.Column([
            ft.Row([
                ft.TextField(prefix_text="f(x) = ", width=220, prefix_style=ft.TextStyle(color=ft.Colors.GREY_200, size=16, weight=ft.FontWeight.BOLD), 
                         border_color=ft.Colors.GREY_200, border_width=2, color=ft.Colors.GREY_200, 
                         cursor_color=ft.Colors.GREY_200, selection_color=ft.Colors.GREY_500, hint_text="Write your equation...", 
                         hint_style=ft.TextStyle(color=ft.Colors.GREY_300), text_align=ft.TextAlign.LEFT),
                ft.IconButton(icon=ft.Icons.SEND, icon_color=ft.Colors.GREY_200, icon_size=20, highlight_color=ft.Colors.RED, hover_color=ft.Colors.GREY_500, on_click=sendPlot)
            ]),
            ft.Container(height=5),
            ft.IconButton(icon=ft.Icons.PASTE, icon_color=ft.Colors.GREY_200, icon_size=20, highlight_color=ft.Colors.RED, hover_color=ft.Colors.GREY_500, on_click=PasteData),
            ft.ListView(expand=1, spacing=10, padding=5, controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("x", size=20, color=ft.Colors.WHITE)),
                        ft.DataColumn(ft.Text("y", size=20, color=ft.Colors.WHITE)),
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

    #Container de ajuste do gráfico
    graphSets = ft.Container(
        bgcolor=ft.Colors.LIGHT_BLUE_200,
        width=300,
        height=300,
        border_radius=10,
        padding=20,
        expand_loose=10,
        content=ft.Column([
            ft.IconButton(ft.Icons.CIRCLE, icon_color=ft.Colors.BLUE, tooltip="Color")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    page.add(
        ft.Text("PLOT LAB", size=50),
        ft.Row([
            mainContainer,
            MatplotlibChart(figure, expand=True),
        ], width=900),
    )


ft.app(main, view=ft.AppView.WEB_BROWSER)