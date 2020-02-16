#!/usr/bin/env python
'''
Copyright (c) 2010 MakerBot Industries

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

'''
This code is meant for needle cutting foam board.
It can work with just the needle cutter or a combination of a needle cutter and a pen.

In the first configuration it uses a shallow cut depth for engraving.
In the second configuration it uses the pen for the engravings.

G0 commands are used for moving the Z axis up and down.
Sx commands are used to move a servo connected to the pen holder.

https://wiki.inkscape.org/wiki/index.php/INX_Parameters
'''

import sys,os
import inkex
from math import *
import getopt
from unicorn.context import GCodeContext
from unicorn.svg_parser import SvgParser

class MyEffect(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)
    self.OptionParser.add_option("--pen-up-cmd",
                      action="store", type="string",
                      dest="pen_up_cmd", default="G0 10",
                      help="Pen Up Command")
    self.OptionParser.add_option("--pen-down-cmd",
                      action="store", type="string",
                      dest="pen_down_cmd", default="G0",
                      help="Pen Down Command")
    self.OptionParser.add_option("--pen-down-angle",
                      action="store", type="float",
                      dest="pen_down_angle", default="6.0",
                      help="Pen Cut Depth")
    self.OptionParser.add_option("--pen-x-offset",
                      action="store", type="float",
                      dest="pen_x_offset", default="2.5",
                      help="Pen X offset")
    self.OptionParser.add_option("-pen-y-offset",
                      action="store", type="float",
                      dest="pen_y_offset", default="1.0",
                      help="Pen Y offset")
    self.OptionParser.add_option("--start-delay",
                      action="store", type="float",
                      dest="start_delay", default="1",
                      help="Delay after pen down command before movement in seconds")
    self.OptionParser.add_option("--stop-delay",
                      action="store", type="float",
                      dest="stop_delay", default="1.0",
                      help="Delay after pen up command before movement in seconds")
    self.OptionParser.add_option("--xy-feedrate",
                      action="store", type="float",
                      dest="xy_feedrate", default="3500.0",
                      help="XY axes feedrate in mm/min")
    self.OptionParser.add_option("--xy-travelrate",
                      action="store", type="float",
                      dest="xy_travelrate", default="7000.0",
                      help="XY axes travelrate in mm/min")
    self.OptionParser.add_option("--z-feedrate",
                      action="store", type="float",
                      dest="z_feedrate", default="150.0",
                      help="Z axis feedrate in mm/min")
    self.OptionParser.add_option("--needle-start-delay",
                      action="store", type="float",
                      dest="needle_start_delay", default="0.0",
                      help="Delay after needle down command before movement in seconds")
    self.OptionParser.add_option("--needle-stop-delay",
                      action="store", type="float",
                      dest="needle_stop_delay", default="0.0",
                      help="Delay after needle up command before movement in seconds")
    self.OptionParser.add_option("--pen-x-offset",
                      action="store", type="float",
                      dest="pen_x_offset", default="0.0",
                      help="X Offset of the pen from normal tool")
    self.OptionParser.add_option("--pen-y-offset",
                      action="store", type="float",
                      dest="pen_y_offset", default="0.0",
                      help="Y Offset of the pen from normal tool")
    self.OptionParser.add_option("--z-height",
                      action="store", type="float",
                      dest="z_height", default="0.0",
                      help="Z axis print height in mm")
    self.OptionParser.add_option("--finished-height",
                      action="store", type="float",
                      dest="finished_height", default="0.0",
                      help="Z axis height after printing in mm")
    self.OptionParser.add_option("--x-home",
                      action="store", type="float",
                      dest="x_home", default="0.0",
                      help="Starting X position")
    self.OptionParser.add_option("--y-home",
                      action="store", type="float",
                      dest="y_home", default="0.0",
                      help="Starting Y position")
    self.OptionParser.add_option("--num-copies",
                      action="store", type="int",
                      dest="num_copies", default="1")
    self.OptionParser.add_option("--continuous",
                      action="store", type="string",
                      dest="continuous", default="false",
                      help="Plot continuously until stopped.")
    self.OptionParser.add_option("--tab",
                      action="store", type="string",
                      dest="tab")

  def output(self):
    self.context.generate()

  def effect(self):
    self.context = GCodeContext(
                           self.options.xy_feedrate,
                           self.options.xy_travelrate,
                           self.options.z_feedrate,
                           self.options.start_delay, 
                           self.options.stop_delay,
                           self.options.needle_start_delay,
                           self.options.needle_stop_delay,
                           self.options.needle_up_position,
                           self.options.needle_cut_position,
                           self.options.needle_score_position,
                           self.options.use_pen,
                           self.options.pen_up_cmd,
                           self.options.pen_down_cmd,
                           self.options.pen_down_angle, 
                           self.options.pen_x_offset,
                           self.options.pen_y_offset,
                           self.options.continuous,
                           self.svg_file)
    parser = SvgParser(self.document.getroot())
    parser.parse()
    for entity in parser.entities:
      entity.get_gcode(self.context)

if __name__ == '__main__':   #pragma: no cover
  e = MyEffect()
  e.affect()
