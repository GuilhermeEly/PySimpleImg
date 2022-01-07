import PySimpleGUI as sg


class MainView:
    def buildLayout(self):
        layout = [
            [
                sg.Frame("Padrão", layout= [
                [
                    sg.Image(filename='', key='image')
                ]]),
                sg.Frame("Feedback", layout = [ 
                [
                    sg.Image(filename='', key='image3')
                ]])      
            ],
            [
                sg.Frame("Diferenças", layout = [ 
                [
                    sg.Image(filename='', key='image2')
                ]]),
                sg.Frame("Diff", layout = [ 
                [
                    sg.Image(filename='', key='image4')
                ]]),
                sg.Frame("Mask", layout = [ 
                [
                    sg.Image(filename='', key='image5')
                ]])
                
            ],
            [
                sg.Frame("", layout= [
                [
                    sg.Button('Camera', size=(10, 1), font='Helvetica 14'),
                    sg.Button('Salvar', size=(10, 1), font='Any 14'),
                    sg.Button('Comparar', size=(10, 1), font='Any 14'),
                    sg.Button('Sair', size=(10, 1), font='Helvetica 14'),
                    sg.Button('Editar', size=(10, 1), font='Any 14')
                ]])
            ]
        ]

        return layout

    def create_window(self):
        return sg.Window('Editar Imagem', layout=self.buildLayout(), modal=True, location=(0, 0))
