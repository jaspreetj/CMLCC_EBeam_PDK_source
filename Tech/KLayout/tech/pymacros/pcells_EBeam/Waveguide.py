"""
This file is part of the SiEPIC-Tools and SiEPIC-EBeam PDK
"""

from pya import *
import pya

class Waveguide(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(Waveguide, self).__init__()
    
    from SiEPIC.utils import load_Waveguides_by_Tech

    self.technology_name = 'EBeam_CMLC'

    # Load all strip waveguides
    self.waveguide_types = load_Waveguides_by_Tech(self.technology_name)   
        
    # declare the parameters

    p = self.param("waveguide_type", self.TypeList, "Waveguide Type", default = self.waveguide_types[0]['name'])
    for wa in self.waveguide_types:
        p.add_choice(wa['name'],wa['name'])
    self.param("path", self.TypeShape, "Path", default = DPath([DPoint(0,0), DPoint(10,0), DPoint(10,10)], 0.5))

    # self.param("length", self.TypeDouble, "Length", default = 0, readonly=True)
    ''' todo - can add calculated values and parameters for user info
    self.param("radius", self.TypeDouble, "Bend Radius", default = 0, readonly=True)
    '''
    
    self.cellName="Waveguide"

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "%s_%s" % (self.cellName, self.path)
  
  def coerce_parameters_impl(self):
#    self.length = self.waveguide_length
    pass                  
  def can_create_from_shape_impl(self):
    return self.shape.is_path()

  def transformation_from_shape_impl(self):
    return Trans(Trans.R0,0,0)

  def parameters_from_shape_impl(self):
    self.path = self.shape.path
        
  def produce_impl(self):
        
    # Make sure the technology name is associated with the layout
    #  PCells don't seem to know to whom they belong!
    if self.layout.technology_name == '':
        self.layout.technology_name = self.technology_name

    # Draw the waveguide geometry, new function in SiEPIC-Tools v0.3.90
    from SiEPIC.utils.layout import layout_waveguide4
    from SiEPIC.utils import get_technology_by_name
    TECHNOLOGY = get_technology_by_name(technology_name)
    LayerDevRecN = layout.layer(TECHNOLOGY['DevRec'])
    from pya import Trans, Text, Point
    self.waveguide_length = layout_waveguide4(self.cell, self.path, self.waveguide_type)


    # Add Pin Order
    layout = self.cell.layout()
    dbu = layout.dbu
    dpath = self.path.to_itype(dbu)
    dpath.unique_points()
    dpt = Point(0,0)
    pts = dpath.get_points()
    pt0= pts[0] - 3*dpt
    t = Trans(0, False, pt0)
    print("points1",pts[0])
    print("points2",self.pts[0])
    text = Text( 'pinOrder:opt1 opt2',t, 0.1, -1)
    text.halign=0
    shape = self.cell.shapes(LayerDevRecN).insert(text)

    print("AMF.%s: length %s um, complete" % (self.cellName, self.waveguide_length))
