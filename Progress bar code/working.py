import PySimpleGUI as sg

class Progress(sg.Column):

    def __init__(self, width=3, height=8, font=("Courier New", 16)):
        self.width  = width
        self.height = height
        self.font   = font
        self.x_unit = sg.Text.char_width_in_pixels(font)
        self.y_unit = sg.Text.char_height_in_pixels(font)
        self.figure = None
        self.size   = self.w, self.y = (self.width + 6) * self.x_unit + 1, (self.height + 1) * self.y_unit + 1
        self.text   = sg.Text("0%", size=4, font=font, justification='center', pad=(0, 0), expand_x=True, key='Percent')
        self.graph  = sg.Graph(self.size, (0, 0), self.size, pad=(0, 0), background_color=sg.theme_background_color(), key='Graph')
        layout = [[self.text], [sg.Push(), self.graph, sg.Push()]]
        super().__init__(layout, pad=(0, 0))

    def initial(self):
        for y, i in enumerate(range(0, 120, 20)):
            self.graph.draw_text(str(i), (3*self.x_unit, y/5*self.height*self.y_unit), font=self.font, color='white', text_location=sg.TEXT_LOCATION_BOTTOM_RIGHT)
            self.graph.draw_line((3*self.x_unit+1, (y/5*self.height+0.5)*self.y_unit), (6*self.x_unit, (y/5*self.height+0.5)*self.y_unit), color='white')
        self.graph.draw_rectangle(
            (6*self.x_unit, (self.height+0.5)*self.y_unit),
            ((6+self.width)*self.x_unit, 0.5*self.y_unit),
            fill_color='white', line_color='white')

    def count(self, value):
        new_figure = self.graph.draw_rectangle(
            (6*self.x_unit+1, (0.5+value/100*self.height)*self.y_unit-1),
            ((6+self.width)*self.x_unit-1, 0.5*self.y_unit+1),
            fill_color='blue')
        if self.figure:
            self.graph.delete_figure(self.figure)
        self.figure = new_figure
        self.text.update(f'{value}%')

progress = Progress()
window = sg.Window('Progress Bar', [[progress]], margins=(0, 0), finalize=True)
progress.initial()
count, step = 0, 4

while True:

    event, values = window.read(timeout=50)

    if event == sg.WIN_CLOSED:
        break
    elif event == sg.TIMEOUT_EVENT:
        count += step
        if count > 100:
            count, step = 100, -2
            continue
        elif count < 0:
            count, step = 0, +2
            continue
        progress.count(count)

window.close()