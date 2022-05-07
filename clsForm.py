#!/usr/bin/env python
import PySimpleGUI as sg
from random import randint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import io
import PIL
import base64

class Form:
    def __init__(self):
        self.NUM_DATAPOINTS = 10000
        self.fig_dict = {'Pyplot Simple': self.PyplotSimple, 'Pyplot Formatstr': self.PyplotFormatstr}
        self.create_layout()

    def create_layout(self):
        # define the form layout
        col_listbox = [[sg.Listbox(values=list(self.fig_dict.keys()), select_mode=sg.SELECT_MODE_EXTENDED, enable_events=True, size=(28, len(list(self.fig_dict))), key='-LISTBOX-')],
               [sg.Exit(size=(5, 2))]]

        image_col = sg.Col([[sg.Image(k=(i,j)) for i in range(4)]for j in range(4)])

        layout = [[sg.Text('Animated Matplotlib', size=(40, 1),
                    justification='center', font='Helvetica 20')],
                [sg.Text('Matplotlib Grid of Plots Using PIL', font=('current 18'))],
                [sg.Col(col_listbox, element_justification='c'),
                image_col],
                [sg.Canvas(size=(240, 80), key='-CANVAS-')],
                [sg.Text('Progress through the data')],
                [sg.Slider(range=(0, self.NUM_DATAPOINTS), size=(60, 10),
                    orientation='h', key='-SLIDER-')],
                [sg.Text('Number of data points to display on screen')],
                [sg.Slider(range=(10, 500), default_value=40, size=(40, 10),
                        orientation='h', key='-SLIDER-DATAPOINTS-')],
                [sg.Button('Exit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]]

        # create the form and show it without the plot
        window = sg.Window('Application - Embedding Matplotlib In PySimpleGUI',
                    layout, finalize=True)
        self.update_layout(window)
        return 
    
    def update_layout(self, window):
        canvas_elem = window['-CANVAS-']
        slider_elem = window['-SLIDER-']
        canvas = canvas_elem.TKCanvas

        fig, ax = self.create_matplotlib()
        fig_agg = self.draw_figure(canvas, fig)
        # make a bunch of random data points
        dpts = [randint(0, 10) for x in range(self.NUM_DATAPOINTS)]

        for i in range(len(dpts)):
            event, values = window.read(timeout=10)
            # print(values)
            if event in ('Exit', None):
                exit(69)

            slider_elem.update(i)       # slider shows "progress" through the data points
            ax.cla()                    # clear the subplot
            ax.grid()                   # draw the grid
            data_points = int(values['-SLIDER-DATAPOINTS-']) # draw this many data points (on next line)
            ax.plot(range(data_points), dpts[i:i+data_points],  color='purple')
            fig_agg.draw()

            figure_w, figure_h = 150, 150
            for i, choice in enumerate(values['-LISTBOX-']):
                # print(i, choice)
                func = self.fig_dict[choice]  # get function to call from the dictionary
                # print(func)
                fig = func()  # call function to get the figure
                image = self.figure_to_image(fig)
                image = self.convert_to_bytes(image, (figure_w, figure_h))
                image = self.convert_to_bytes(image, (figure_w, figure_h))
                window[(i%4, i//4)].update(data=image)

        window.close()

    def figure_to_image(self, figure):
        plt.close('all')        # erases previously drawn plots
        canv = FigureCanvasAgg(figure)
        buf = io.BytesIO()
        canv.print_figure(buf, format='png')
        if buf is None:
            return None
        buf.seek(0)
        return buf.read()

    def draw_figure(self, canvas, figure, loc=(0, 0)):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    def convert_to_bytes(self, file_or_bytes, resize=None):
        if isinstance(file_or_bytes, str):
            img = PIL.Image.open(file_or_bytes)
        else:
            try:
                img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
            except Exception as e:
                dataBytesIO = io.BytesIO(file_or_bytes)
                img = PIL.Image.open(dataBytesIO)

        cur_width, cur_height = img.size
        if resize:
            new_width, new_height = resize
            scale = min(new_height/cur_height, new_width/cur_width)
            img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
        with io.BytesIO() as bio:
            img.save(bio, format="PNG")
            del img
            return bio.getvalue()

    def create_matplotlib(self):
        # draw the initial plot in the window
        fig = Figure()
        ax = fig.add_subplot(121)
        ax.set_xlabel("X axis")
        ax.set_ylabel("Y axis")
        ax.grid()
        return fig, ax

    def PyplotSimple(self):
        # evenly sampled time .2 intervals
        t = np.arange(0., 5., 0.2)  # go from 0 to 5 using .2 intervals
        # red dashes, blue squares and green triangles
        plt.plot(t, t, 'r--', t, t ** 2, 'bs', t, t ** 3, 'g^')
        fig = plt.gcf()  # get the figure to show
        return fig

    def PyplotHistogram(self):
        np.random.seed(0)

        n_bins = 10
        x = np.random.randn(1000, 3)

        fig, axes = plt.subplots(nrows=2, ncols=2)
        ax0, ax1, ax2, ax3 = axes.flatten()

        colors = ['red', 'tan', 'lime']
        ax0.hist(x, n_bins, normed=1, histtype='bar', color=colors, label=colors)
        ax0.legend(prop={'size': 10})
        ax0.set_title('bars with legend')

        ax1.hist(x, n_bins, normed=1, histtype='bar', stacked=True)
        ax1.set_title('stacked bar')

        ax2.hist(x, n_bins, histtype='step', stacked=True, fill=False)
        ax2.set_title('stack step (unfilled)')

        # Make a multiple-histogram of data-sets with different length.
        x_multi = [np.random.randn(n) for n in [10000, 5000, 2000]]
        ax3.hist(x_multi, n_bins, histtype='bar')
        ax3.set_title('different sample sizes')

        fig.tight_layout()
        return fig

    def PyplotFormatstr(self):
        def f(t):
            return np.exp(-t) * np.cos(2 * np.pi * t)

        t1 = np.arange(0.0, 5.0, 0.1)
        t2 = np.arange(0.0, 5.0, 0.02)

        plt.figure(1)
        plt.subplot(211)
        plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')

        plt.subplot(212)
        plt.plot(t2, np.cos(2 * np.pi * t2), 'r--')
        fig = plt.gcf()  # get the figure to show
        return fig

def main():
    form = Form()
    # form.create_layout()

if __name__ == "__main__":
    main()
