class AreaOfInterest:
  def __init__(self, name, area):
    self.name = name
    self.area = area                # (xmin, ymin, xmax, ymax)
    self.annotation_lines = []      # annotate with lines list of lines ((x1, y1), (x2, y2))
    self.annotate_cross_hairs = []  # annotate with cross-hairs list of points ((x1, y1))
    self.annotate_circles = []      # annotate with circles list of centers ((x1, y1))
    self.annotate_text = []         # list of text messages to be added to the aoi

  def center(self):
    return ((self.area[0] + self.area[2]) / 2.0, (self.area[1] + self.area[3]) / 2.0)

  def contains(self, point):
    return self.area[0] < point[0] < self.area[2] and self.area[1] < point[1] < self.area[3]
