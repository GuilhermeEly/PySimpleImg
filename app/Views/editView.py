import PySimpleGUI as sg


class EditView:
    def buildLayout(self):
        sliderSize = (30, 5)
        textSize = (10, 1)
        textConf = 'Helvetica 8 italic'
        titleTextConfig = 'Helvetica 8 bold'
        layoutEdit = [
                [
                    sg.Frame("Edit", layout= [
                    [
                        sg.Image(filename='', key='editImage')
                    ]]),
                    sg.Frame("Opções", layout= [
                    [
                        sg.Column(layout=
                        [
                            [
                                sg.Text("Área válida", font = titleTextConfig)
                            ],
                            [
                                sg.Text("X0:", font = textConf, s = textSize),
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='originX', size = sliderSize, default_value=0),
                                sg.Text("X1:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='sizeX', size = sliderSize, default_value=50),
                            ],
                            [
                                sg.Text("Y0:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='originY', size = sliderSize, default_value=0),
                                sg.Text("Y1:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 10000), tick_interval=100, orientation='h', key='sizeY', size = sliderSize, default_value=50),
                            ],
                            [
                                sg.Text("Configurações", font = titleTextConfig)
                            ],
                            [
                                sg.Text("Foco:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=5,  orientation='h', key='editFocus', size = sliderSize, default_value=50),
                                sg.Text("Brilho:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editBrightness', size = sliderSize, default_value=50)
                            ],
                            [
                                sg.Text("Contraste:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editContrast', size = sliderSize, default_value=50),
                                sg.Text("Saturação:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 255), tick_interval=51, resolution=1,  orientation='h', key='editSaturation', size = sliderSize, default_value=50)
                            ],
                            [
                                sg.Text("Erro:", font = textConf, s = textSize), 
                                sg.Slider(font = textConf, range=(0, 2000), orientation='h', key='editArea', size = sliderSize, default_value=50)
                            ],
                        ], size=(600, 280)),
                        
                    ]]),
                ],
                [
                    sg.Frame("", layout= [
                    [
                        sg.Button('Salvar', size=(10, 1), font='Helvetica 14'),
                    ]])
                ]
            ]

        return layoutEdit

    def create_window(self):
        return sg.Window('Editar Imagem', layout=self.buildLayout(), modal=True, location=(0, 0))
