import sys, os
# sys.path.append(os.path.dirname(os.path.realpath(__file__) + \
#                 os.path.sep + os.path.pardir + \
#                 os.path.sep + os.path.pardir))
# this is specific the location of pypif, since I haven't
# installed pypif
sys.path.append('/Users/bkappes/src/citrine/pypif')
from pypif import pif
from alloy import AlloyBase

class Inconel718(AlloyBase):
    def __init__(self, **kwds):
        super(Inconel718, self).__init__(**kwds)
        # set names
        names = ['Inconel', 'Inconel 718', '718', 'UNS N07718',
                 'W.Nr. 2.4668', 'AMS 5596', 'ASTM B637']
        self.names = names
        # set references
        url='http://www.specialmetals.com/documents/Inconel%20alloy%20718.pdf'
        references = [pif.Reference(url=url)]
        self.references = references
        # preparation
        if 'preparation' in kwds:
            self.preparation = kwds['preparation']
        else:
            self.preparation = []
        # set composition
        balance = {'low' : 100., 'high' : 100.}
        # at some point, allow the user to tweak the composition on an
        # element-by-element basis by passing something to the class
        # alloy compositions are typically defined in weight/mass percent
        # with one element set by "balance".
        composition = []
        for elem, (low, high) in (('Ni', (50., 55.)),
                                  ('Cr', (17., 21.)),
                                  ('Nb', (4.75, 5.5)),
                                  ('Mo', (2.8, 3.3)),
                                  ('Ti', (0.65, 1.15)),
                                  ('Al', (0.2, 0.8)),
                                  ('Co', (0.0, 1.0)),
                                  ('C',  (0.0, 0.08)),
                                  ('Mn', (0.0, 0.35)),
                                  ('Si', (0.0, 0.35)),
                                  ('P',  (0.0, 0.015)),
                                  ('S',  (0.0, 0.015)),
                                  ('B',  (0.0, 0.006)),
                                  ('Cu', (0.0, 0.30))):
            balance['low']  -= high
            balance['high'] -= low
            component = pif.Composition(element=elem,
                ideal_weight_percent=pif.Scalar(minimum=low, maximum=high))
            composition.append(component)
        assert(balance['low'] >= 0.0)
        assert(balance['high'] >= 0.0)
        component = pif.Composition(element='Fe',
            ideal_weight_percent=pif.Scalar(minimum=balance['low'],
                                            maximum=balance['high']))
        composition.append(component)
        self.composition = composition
#end 'class Inconel718(pif.Alloy):'
