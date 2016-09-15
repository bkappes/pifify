from ...samples import FaustsonSample
from itertools import product


class CylinderPlate2mmX4mm(object):
    skip = ((ord('A'), 1), (ord('B'), 1), (ord('X'), 1), (ord('Y'), 1),
            (ord('A'), 2), (ord('Y'), 2),
            (ord('C'), 3), (ord('D'), 3), (ord('V'), 3), (ord('W'), 3),
            (ord('C'), 23), (ord('D'), 23), (ord('V'), 23), (ord('W'), 23),
            (ord('A'), 24), (ord('Y'), 24),
            (ord('A'), 25), (ord('B'), 25), (ord('X'), 25), (ord('Y'), 25))
    phi = dict(zip(
        xrange(1, 25+1),
        (45., 45., 45.,
         0.,
         90., 90., 90., 90.,
         45., 45., 45., 45.,
         0.,
         90., 90., 90., 90.,
         45., 45., 45., 45.,
         0.,
         90., 90., 90.)))
    theta = dict(zip(
        xrange(1, 25+1),
        (180., 270., 90.,
         0.,
         90., 45., 0., 135.,
         0., 180., 270., 90.,
         0.,
         90., 45., 0., 135.,
         0., 180., 270., 90.,
         0.,
         90., 45., 0.)))

    def __init__(self, *args, **kwds):
        super(CylinderPlate2mmX4mm, self).__init__(*args, **kwds)
        self.samples = []
        for col, row in product(xrange(ord('A'), ord('Y')+1),
                                xrange(1, 25+1)):
            if (col, row) in self.skip:
                continue
            sample = FaustsonSample()
            vpos, hpos = self.get_cartesian(row, col)
            setattr(sample, 'RD', hpos)
            setattr(sample, 'TD', vpos)
            setattr(sample, 'col', chr(col))
            setattr(sample, 'row', row)
            setattr(sample, 'laserIndex', -1) # No explicit laser index
            setattr(sample, 'innerSkinLaserPower', 0.0)
            setattr(sample, 'innerSkinLaserSpeed', 0.0)
            setattr(sample, 'innerSkinLaserSpot', 30.0)
            setattr(sample, 'innerSkinOverlap', 0.15)
            setattr(sample, 'nlayers', 195)
            setattr(sample, 'polar', self.phi[row])
            setattr(sample, 'powderSize', (10,45))
            setattr(sample, 'plateMaterial', 'P20 steel')
            setattr(sample, 'sieveCount', 0)
            setattr(sample, 'skinLaserPower', 0.0)
            setattr(sample, 'skinLaserSpeed', 0.0)
            setattr(sample, 'skinLaserSpot', 30.0)
            setattr(sample, 'skinOverlap', 0.16)
            setattr(sample, 'azimuth', self.theta[row])
            setattr(sample, 'virgin', 100.)
            # done -- add the sample
            self.samples.append(sample)

    def __iter__(self):
        for sample in self.samples:
            yield sample

    def get_cartesian(self, row, col):
        cls = type(self)
        spacing = 11.54
        return (spacing*row, spacing*col)
#end 'class CylinderPlate2mmX4mm(object):'


class P001B001(CylinderPlate2mmX4mm):
    def __init__(self, *args, **kwds):
        super(P001B001, self).__init__(*args, **kwds)
        for sample in self:
            setattr(sample, 'plate', 1)
            setattr(sample, 'build', 1)
            # annealed samples
            sample.alloy.anneal(1253, duration=1, description='solution anneal')
            sample.alloy.cool(1253, description='oven cool')
            sample.alloy.anneal(993, duration=8, description='aging-1')
            sample.alloy.cool(993, duration=2, Tstop=893, description='aging-2')
            sample.alloy.anneal(893, duration=8, description='aging-3')
#end 'class P001B001(CylinderPlate2mmX4mm)'


class P002B001(CylinderPlate2mmX4mm):
    def __init__(self, *args, **kwds):
        super(P002B001, self).__init__(*args, **kwds)
        for sample in self:
            setattr(sample, 'plate', 2)
            setattr(sample, 'build', 1)
#end 'class P002B001(CylinderPlate2mmX4mm)'


class P003B001(CylinderPlate2mmX4mm):
    def __init__(self, *args, **kwds):
        super(P003B001, self).__init__(*args, **kwds)
        for sample in self:
            setattr(sample, 'plate', 3)
            setattr(sample, 'build', 1)
#end 'class P003B001(CylinderPlate2mmX4mm)'


class P004B001(CylinderPlate2mmX4mm):
    def __init__(self, *args, **kwds):
        super(P004B001, self).__init__(*args, **kwds)
        for sample in self:
            setattr(sample, 'plate', 4)
            setattr(sample, 'build', 1)
            setattr(sample, 'virgin', 20.0)
#end 'class P004B001(CylinderPlate2mmX4mm)'


class P005B001(CylinderPlate2mmX4mm):
    def __init__(self, *args, **kwds):
        super(P005B001, self).__init__(*args, **kwds)
        for sample in self:
            setattr(sample, 'plate', 5)
            setattr(sample, 'build', 1)
            setattr(sample, 'laserIndex', 1)
            setattr(sample, 'virgin', 20.0)
#end 'class P005B001(CylinderPlate2mmX4mm)'


class P006B001(CylinderPlate2mmX4mm):
    def __init__(self, *args, **kwds):
        super(P006B001, self).__init__(*args, **kwds)
        for sample in self:
            setattr(sample, 'plate', 6)
            setattr(sample, 'build', 1)
            setattr(sample, 'laserIndex', 2)
            setattr(sample, 'virgin', 20.0)
#end 'class P006B001(CylinderPlate2mmX4mm)'
