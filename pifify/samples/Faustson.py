import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__) + \
                os.path.sep + os.path.pardir))
# this is specific the location of pypif, since I haven't
# installed pypif
try:
    from pypif import pif
except ImportError:
    sys.path.append('/Users/bkappes/src/citrine/pypif')
    from pypif import pif
from .base import SampleMeta, preparation_factory, property_factory
from ..materials.inconel import Inconel718

class FaustsonSample(pif.System):
    __metaclass__ = SampleMeta # use the SampleMeta API
    # Properties relevant to the samples produced at Faustson. This stores a
    # dictionary of
    #   property : conversion
    # entries. *conversion* takes one or more arguments and returns the
    # appropriate type for *property*.

    _prep = {
        'annealed' : \
            preparation_factory('annealed'),
        'build' : \
            preparation_factory('build'),
        'col' : \
            preparation_factory('column'),
        'laserIndex' : \
            preparation_factory('laser ID'),
        'innerSkinLaserPower' : \
            preparation_factory('inner skin laser power', units='%'),
        'innerSkinLaserSpeed' : \
            preparation_factory('inner skin laser speed', units='%'),
        'innerSkinLaserSpot' : \
            preparation_factory('inner skin laser spot', units='$\mu$m'),
        'innerSkinOverlap' : \
            preparation_factory('inner skin overlap', units='mm'),
        'nlayers' : \
            preparation_factory('number of layers'),
        'polar' : \
            preparation_factory('polar angle', units='${}^\circ$'),
        'powderSize' : lambda lohi : \
            pif.Property(name = 'powder size',
                         scalars = pif.Scalar(minimum=lohi[0],
                                              maximum=lohi[1]),
                         units='$\mu$m'),
        'plate' : \
            preparation_factory('plate number'),
        'plateMaterial' : \
            preparation_factory('plate material'),
        'row' : \
            preparation_factory('row'),
        'sieveCount' : \
            preparation_factory('sieve count'),
        'skinLaserPower' : \
            preparation_factory('skin laser power', units='%'),
        'skinLaserSpeed' : \
            preparation_factory('skin laser speed', units='%'),
        'skinLaserSpot' : \
            preparation_factory('skin laser spot', units='$\mu$m'),
        'skinOverlap' : \
            preparation_factory('skin overlap', units='mm'),
        'azimuth' : \
            preparation_factory('azimuth angle', units='${}^\circ$'),
        'virgin' : \
            preparation_factory('virgin powder', units='%'),
        'RD' : \
            preparation_factory('blade direction', units='mm'),
        'TD' : \
            preparation_factory('transverse direction', units='mm')
    }

    def __init__(self, *args, **kwds):
        super(FaustsonSample, self).__init__(*args, **kwds)
        self.sub_systems = [Inconel718()]
        self.preparation = [pif.ProcessStep(
            name='printing',
            details=[],
            instrument=[pif.Instrument(
                name='Faustson M2',
                model='M2 Cusing',
                producer='ConceptLaser',
                url='http://www.conceptlaserinc.com/machines/'
            )]
        )]
        #self.properties = [
        #    pif.Property(..., category='materials'),
        #    pif.Property(..., category='engineering')
        #]

    @property
    def alloy(self):
        return self.sub_systems[0]

    @property
    def printing(self):
        return self.preparation[0]
#end 'class FaustsonSample(pif.System):'
