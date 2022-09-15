import json
from copy import deepcopy
from importlib import resources

import ipywidgets as widgets
import numpy as np
from jsonschema import validate
from traitlets import Bool, Dict, Float, List, Unicode

# See js/lib/example.js for the frontend counterpart to this file.

with resources.open_text("widget_bandsplot.schemas", "pdos.json") as fh:
    PDOS_SCHEMA = json.load(fh)


@widgets.register
class BandsPlotWidget(widgets.DOMWidget):
    """A Jupyter widget to plot bandstructures and DOS."""

    # Name of the widget view class in front-end
    _view_name = Unicode("BandsplotView").tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode("BandsplotModel").tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode("widget-bandsplot").tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode("widget-bandsplot").tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode("^0.2.4").tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode("^0.2.4").tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged
    # with `sync=True` is automatically synced to the frontend *any* time
    # it changes in Python. It is synced back to Python from the frontend
    # *any* time the model is touched.
    value = Unicode("This is bandsplot!").tag(sync=True)

    # Json fils for the bandstructures
    bands = List().tag(sync=True)

    # Json file for the DOS plot
    dos = Dict().tag(sync=True)

    # yLimit for the plot
    energy_range = Dict({"ymin": -10.0, "ymax": 10.0}).tag(sync=True)
    dos_range = List().tag(sync=True)

    # Band and DOS Fermi energy
    band_fermienergy = List().tag(sync=True)
    dos_fermienergy = Float().tag(sync=True)

    # Visiblity for the Fermi energy level
    plot_fermilevel = Bool(True).tag(sync=True)

    # The Legend for the density of states
    show_legend = Bool(True).tag(sync=True)

    # Whether is spin polarized calculations
    spin_polarized = Bool(False).tag(sync=True)

    def __init__(
        self,
        bands=None,
        dos=None,
        fermi_energy=None,
        show_legend=True,
        plot_fermilevel=True,
        energy_range=None,
    ):
        if energy_range is None:
            energy_range = {"ymin": -10.0, "ymax": 10.0}

        if bands is None and dos is None:
            raise ImportError("You need give band structure or DOS files.")

        super().__init__(
            show_legend=show_legend,
            plot_fermilevel=plot_fermilevel,
            energy_range=energy_range,
        )

        if bands is not None:
            self.bands = bands

            for i in bands:
                self.band_fermienergy.append(i["fermi_level"])

        if dos is not None:
            # validate the pdos inputs on schema,
            # raise validate error when not conform with schema
            validate(instance=dos, schema=PDOS_SCHEMA)

            self.dos_fermienergy = dos["fermi_energy"]
            temp_dos = deepcopy(dos)

            ymin = []
            ymax = []
            for i, j in enumerate(temp_dos["dos"]):
                tx = j["x"]
                ty = j["y"]

                tx = np.array(tx)
                ty = np.array(ty)

                index = np.where(
                    np.logical_and(
                        tx > energy_range["ymin"] + self.dos_fermienergy,
                        tx < energy_range["ymax"] + self.dos_fermienergy,
                    )
                )

                ymin.append(min(ty[index]))
                ymax.append(max(ty[index]))

            self.dos_range = [min(ymin)*1.05, max(ymax)*1.05]

            #     temp_dos["dos"][i]["x"] = tx[index].tolist()
            #     temp_dos["dos"][i]["y"] = ty[index].tolist()

            self.dos = deepcopy(temp_dos)
