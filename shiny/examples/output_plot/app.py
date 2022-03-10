from shiny import *
from shiny.types import ImgData
import numpy as np
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.input_slider(
        "n", "input_slider()", min=10, max=100, value=50, step=5, animate=True
    ),
    ui.output_plot("p"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_plot()
    def p():
        np.random.seed(19680801)
        x_rand = 100 + 15 * np.random.randn(437)
        fig, ax = plt.subplots()
        ax.hist(x_rand, int(input.n()), density=True)
        return fig


app = App(app_ui, server)