from math import *
import sys

class GCodeContext:
    def __init__(self, xy_feedrate, xy_travelrate, z_feedrate, start_delay, stop_delay, needle_start_delay, needle_stop_delay, needle_up_position, needle_cut_position, needle_score_position, use_pen, pen_up_cmd, pen_down_cmd, pen_down_angle, pen_x_offset, pen_y_offset, continuous, file):
    #def __init__(self, xy_feedrate, xy_travelrate, start_delay, stop_delay, pen_up_cmd, pen_down_cmd, pen_down_angle, pen_score_angle, pen_mark_angle, continuous, file):
      self.xy_feedrate = xy_feedrate
      self.xy_travelrate = xy_travelrate
      self.start_delay = start_delay
      self.stop_delay = stop_delay
      self.needle_start_delay = needle_start_delay
      self.needle_stop_delay = needle_stop_delay
      self.needle_up_position = needle_up_position
      self.needle_cut_position = needle_cut_position
      self.needle_score_position = needle_score_position
      self.use_pen = use_pen
      self.pen_up_cmd = pen_up_cmd
      self.pen_down_cmd = pen_down_cmd
      self.pen_down_angle = pen_down_angle
      self.pen_x_offset = pen_x_offset
      self.pen_y_offset = pen_y_offset
      #self.pen_score_angle = pen_score_angle
      #self.pen_mark_angle = pen_mark_angle
      self.finished_height = 0
      self.z_feedrate = z_feedrate
      self.x_home = 0
      self.y_home = 0
      self.z_height = 0
      self.num_pages = 1
      self.continuous = continuous
      self.file = file
      
      self.drawing = False
      self.last = None

      self.preamble = [
        # "G4 P1 (Scribbled version of %s @ %.2f)" % (self.file, self.xy_feedrate),
        # "G4 P1 ( %s )" % " ".join(sys.argv),
        "%s (Pen Up)" % self.pen_up_cmd,
        "G21 (metric ftw)",
        "G90 (absolute mode)",
        "G92 X%.2f Y%.2f Z%.2f (you are here)" % (self.x_home, self.y_home, self.z_height),
        "G0 F%0.2f (Travel Feed Rate)" % self.xy_travelrate,
        "G1 F%0.2f (Cut Feed Rate)" % self.xy_feedrate,
        ""
      ]

      self.postscript = [
        "",
				"(end of print job)",
				"%s (pen up)" % (self.pen_up_cmd),
				"G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay),
				"G0 X%0.2F Y%0.2F F%0.2F (go home)" % (self.x_home, self.y_home, self.xy_travelrate),
				# "M18 (drives off)",
      ]

      self.registration = [
        "%s Z-%d (pen down)" % (self.pen_down_cmd, self.pen_down_angle),
        "G4 P%d (wait %dms)" % (self.start_delay, self.start_delay),
        "%s (pen up)" % (self.pen_up_cmd),
        "G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay),
        # "M18 (disengage drives)",
        # "M01 (Was registration test successful?)",
        # "M17 (engage drives if YES, and continue)",
        ""
      ]

      self.sheet_header = [
        "(start of sheet header)",
        "G92 X%.2f Y%.2f Z%.2f (you are here)" % (self.x_home, self.y_home, self.z_height),
      ]

      self.sheet_footer = [
        "(Start of sheet footer.)",
        "%s (pen up)" % (self.pen_up_cmd),
        "G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay),
        "G91 (relative mode)",
        "G0 Z15 F%0.2f" % (self.z_feedrate),
        "G90 (absolute mode)",
        "G0 X%0.2f Y%0.2f F%0.2f" % (self.x_home, self.y_home, self.xy_feedrate),
        # "M01 (Have you retrieved the print?)",
        "(machine halts until 'okay')",
        "G4 P%d (wait %dms)" % (self.start_delay, self.start_delay),
        "G91 (relative mode)",
        "G0 Z-15 F%0.2f (return to start position of current sheet)" % (self.z_feedrate),
        "G0 Z-0.01 F%0.2f (move down one sheet)" % (self.z_feedrate),
        "G90 (absolute mode)",
        # "M18 (disengage drives)",
        "(End of sheet footer)",
      ]

      self.loop_forever = [ "M30 (Plot again?)" ]

      self.codes = []

    def generate(self):
      if self.continuous == 'true':
        self.num_pages = 1

      codesets = [self.preamble]
      if (self.continuous == 'true' or self.num_pages > 1):
        codesets.append(self.sheet_header)
      codesets.append(self.codes)
      if (self.continuous == 'true' or self.num_pages > 1):
        codesets.append(self.sheet_footer)

      if self.continuous == 'true':
        codesets.append(self.loop_forever)
        for codeset in codesets:
          for line in codeset:
            print line
      else:
        for p in range(0,self.num_pages):
          for codeset in codesets:
            for line in codeset:
              print line
          for line in self.postscript:
            print line

    def start(self, cut_type):
      if cut_type == 2:
        self.codes.append("%s Z-%0.2F (pen down score)" % (self.pen_down_cmd, self.pen_score_angle))
      elif cut_type == 3:
        self.codes.append("%s Z-%0.2F (pen down draw)" % (self.pen_down_cmd, self.pen_mark_angle))
      else:
        self.codes.append("%s Z-%0.2F (pen down through)" % (self.pen_down_cmd, self.pen_down_angle))
      self.codes.append("G4 P%d (wait %dms)" % (self.start_delay, self.start_delay))
      self.drawing = True

    def stop(self):
      self.codes.append("%s (Pen Up)" % self.pen_up_cmd)
      self.codes.append("G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay))
      self.drawing = False

    def go_to_point(self, x, y, stop=False):
      if self.last == (x,y):
        return
      if stop:
        return
      else:
        if self.drawing:
            self.codes.append("%s (Pen Up)" % self.pen_up_cmd)
            self.codes.append("G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay))
            self.drawing = False
        self.codes.append("G0 X%.2f Y%.2f " % (x,y))
      self.last = (x,y)
	
    def draw_to_point(self, x, y, stop=False):
      if self.last == (x,y):
          return
      if stop:
        return
      else:
        if self.drawing == False:
            self.codes.append("%s Z-%0.2F (pen down)" % (self.pen_down_cmd, self.pen_down_angle))
            self.codes.append("G4 P%d (wait %dms)" % (self.start_delay, self.start_delay))
            self.drawing = True
        self.codes.append("G1 X%0.2f Y%0.2f " % (x,y))
      self.last = (x,y)
