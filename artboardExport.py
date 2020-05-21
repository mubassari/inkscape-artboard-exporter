#!/usr/bin/env python

import os

import inkex
from inkex.command import inkscape
from inkex.colors import Color

class ExportArtboards(inkex.EffectExtension):

    def __init__(self):
        super(ExportArtboards, self).__init__()


    def add_arguments(self, pars):
        pars.add_argument("--tab")
        pars.add_argument("--dpi", type=int, help="Dots per inch (96 default)")
        pars.add_argument("--layer", type=str, help="Layer with rects or path in it")
        pars.add_argument("--resize", type=inkex.Boolean, help="Resize Export")
        pars.add_argument("--sizes", type=str, help="resizes export with comma separated")
        pars.add_argument("--bg", type=inkex.Boolean, help="Custom Background Color")
        pars.add_argument("--color", help="Color with RGB (opacity will avoid here)")
        pars.add_argument("--opacity", help="Transparency for color")
        pars.add_argument("--directory", help="Existing destination directory")
        pars.add_argument("--filename", type=str, default="{label} {dpi} {size}", help="Input Filename format")
        pars.add_argument("--overwrite", type=inkex.Boolean, help="Overwrite existing exports?")

    def effect(self):
        layer, hide = self.getLayer(self.options.layer)

        # check if directiry isn't created
        if not os.path.isdir(self.options.directory):
            os.makedirs(self.options.directory)
        # check if size is checked but input is blank
        if self.options.resize and self.options.sizes is None:
            raise inkex.AbortExtension("Please input size!")
        # check if artboard is wrong
        elif layer is None:
            raise inkex.AbortExtension("Artboard: '{}' does not exist.\nMake sure you write the input correctly!".format(self.options.layer))
        # check if DPI is blank
        elif self.options.dpi is None:
            raise inkex.AbortExtension("Please input DPI!")
        # check if artboard is not hide or it's opacity = 1
        elif self.options.bg:
            if hide:
                raise inkex.AbortExtension("Please hide or change opacity of your Artboard layer (not object inside them)!")

        for num, node in enumerate(layer, start=1):
            dpi = self.options.dpi
            if self.options.resize:
                for size in self.options.sizes.split(","):
                    size = size.strip()
                    if size.isdigit():
                        resize = int(dpi) * int(size)
                        self.exportNode(node, resize, num, size)
            else:
                self.exportNode(node, dpi, num)

        return self.document

    def getLayer(self, layerName):
        hide = False
        layer = None
        layerPlace = self.document.findall(inkex.addNS('g', 'svg'))
        for nodes in layerPlace:
            if nodes.label == layerName:
                layer = nodes
                style = dict(inkex.Style.parse_str(nodes.attrib['style']))
                if style.get('opacity') == '1' and style.get('display') != 'none':
                    hide = True
        return layer, hide
        
    def exportNode(self, node, dpi=None, num='1', size=None):
        skip, kwargs = self.formatExport(node, dpi, num, size)
        if skip:
            raise inkex.AbortExtension("File is available in destination.\nPlease change directory location or make sure overwrite option is checked!")

        svgFile = self.options.input_file
        inkscape(svgFile, **kwargs)
        
    def formatExport(self, node, dpi=None, num='1', size=None):
        directory = self.options.directory
        nodeId = node.attrib["id"]
        resize = '' if size is None else 'x'+size
        label = self.getLabel(nodeId)
        color = self.getColor(self.options.color)
        opacity = float(self.options.opacity) * 0.01
        dpiLabel= str(self.options.dpi)+"DPI"
        formatName = self.options.filename+".png"
        fullName = formatName.format(label=label, dpi=dpiLabel, size=resize)
        fileName = os.path.join(directory, fullName)
        if self.options.overwrite or not os.path.exists(fileName):
            skip = False
            kwargs = {'export-id': nodeId, 'export-filename': fileName, 'export-dpi': dpi}
            if self.options.bg:
                kwargs['export-background'] = color
                kwargs['export-background-opacity'] = opacity
            return skip, kwargs
        else:
            skip = True
            return skip, {}

    def getColor(self, color):
        color = hex(int(color))[2:8]
        color = color.rjust(6, '0')

        color = '#'+color.upper()
        return color

    def getLabel(self, nodeId):
        labelValue = None
        for node in self.document.findall(inkex.addNS('g', 'svg')):
            if node.label == self.options.layer:
                for path in node.findall(inkex.addNS('rect', 'svg')):
                    if path.attrib["id"] == nodeId:
                        labelValue = path.label if path.label is not None else path.attrib["id"]
                for path in node.findall(inkex.addNS('path', 'svg')):
                    if path.attrib["id"] == nodeId:
                        labelValue = path.label if path.label is not None else path.attrib["id"]
        return labelValue

if __name__ == "__main__":
    ExportArtboards().run()