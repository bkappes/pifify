#!/usr/bin/env python
"""
DESCRIPTION

    Converts a CSV-formatted input file into Citrine's PIF format.

EXAMPLES

    TODO: Show some examples of how to use this script.
"""

from __future__ import division

import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__) + \
                os.path.sep + os.path.pardir))
# this is specific the location of pypif, since I haven't
# installed pypif
sys.path.append('/Users/bkappes/src/citrine/pypif')
import textwrap, traceback, argparse, re
import time
import shutil
import numpy as np
from pypif import pif
from materials.inconel import Inconel718

class SampleMeta(type):
    """
    Ensure a common interface for all sample classes, specifically,
    this ensures that all classes that use *SampleMeta* as a metaclass
    have a __getattr__ and a __setattr__ that automatically adds getter
    setter properties (practically -- this doesn't actually use the python
    property object).

    To use this metaclass, simply include:

        __metaclass__ = SampleMeta

    in any class that is to use this interface.
    """
    _props = {}

    def __new__(cls, name, parents, dct):
        dct['__getattr__'] = SampleMeta.getattr
        dct['__setattr__'] = SampleMeta.setattr
        return super(SampleMeta, cls).__new__(cls, name, parents, dct)

    @staticmethod
    def getattr(inst, key):
        cls = type(inst)
        if key in cls._props:
            attr = '_{}'.format(key)
            return inst.__dict__.get(attr, None)
        else:
            return inst.__dict__[key]

    @staticmethod
    def setattr(inst, key, *args):
        cls = type(inst)
        if key in cls._props:
            attr = '_{}'.format(key)
            value = cls._props[key](*args)
        else:
            attr = key
            value = args[0]
        super(cls, inst).__setattr__(attr, value)
#end 'class SampleMeta(type):'

class FaustsonSample(pif.System):
    __metaclass__ = SampleMeta # use the SampleMeta API
    # Properties relevant to the samples produced at Faustson. This stores a
    # dictionary of
    #   property : conversion
    # entries. *conversion* takes one or more arguments and returns the
    # appropriate type for *property*.
    _props = {
        'annealed' : lambda x : pif.Scalar(x),
        'build' : lambda x : pif.Scalar(x),
        'column' : lambda x : pif.Scalar(x),
        'innerSkinLaserPower' : lambda x : \
            pif.Property(name = 'inner skin laser power',
                         scalars = [pif.Scalar(x)],
                         units = ['%']),
        'innerSkinLaserSpeed' : lambda x : \
            pif.Property(name = 'inner skin laser speed',
                         scalars = [pif.Scalar(x)],
                         units = ['%']),
        'innerSkinLaserSpot' : lambda x : \
            pif.Property(name = 'inner skin laser spot',
                         scalars = [pif.Scalar(x)],
                         units = ['$\mu$m']),
        'innerSkinOverlap' : lambda x : \
            pif.Property(name = 'inner skin overlap',
                         scalars = [pif.Scalar(x)],
                         units = ['mm']),
        'nlayers' : lambda x : pif.Scalar(x),
        'polar' : lambda x : \
            pif.Property(name = 'polar',
                         scalars = [pif.Scalar(x)],
                         units = ['degrees']),
        'powderSize' : lambda low, high : \
            pif.Property(name = 'powder size',
                         scalars = [pif.Scalar(minimum=low, maximum=high)],
                         units=['$\mu$m']),
        'plate' : lambda x : pif.Scalar(x),
        'row' : lambda x : pif.Scalar(x),
        'sieveCount' : lambda x : pif.Scalar(x),
        'skinLaserPower' : lambda x : \
            pif.Property(name = 'skin laser power',
                         scalars = [pif.Scalar(x)],
                         units = ['%']),
        'skinLaserSpeed' : lambda x : \
            pif.Property(name = 'skin laser speed',
                         scalars = [pif.Scalar(x)],
                         units = ['%']),
        'skinLaserSpot' : lambda x : \
            pif.Property(name = 'skin laser spot',
                         scalars = [pif.Scalar(x)],
                         units = ['$\mu$m']),
        'skinOverlap' : lambda x : \
            pif.Property(name = 'skin overlap',
                         scalars = [pif.Scalar(x)],
                         units = ['mm']),
        'azimuth' : lambda x : \
            pif.Value(name = 'azimuth',
                      scalars = [pif.Scalar(x)],
                      units = ['degrees']),
        'virgin' : lambda x : \
            pif.Value(name = 'virgin powder',
                      scalars = [pif.Scalar(x)],
                      units = ['%']),
        'RD' : lambda x : \
            pif.Value(name = 'rolling direction',
                      scalars = [pif.Scalar(x)],
                      units = ['mm']),
        'TD' : lambda x : \
            pif.Value(name = 'transverse direction',
                      scalars = [pif.Scalar(x)],
                      units = ['mm'])
    }
    def __init__(self, *args, **kwds):
        super(FaustsonSample, self).__init__(*args, **kwds)
        self.alloy = Inconel718()
        self.instrument = pif.Instrument(
            name='Faustson M2',
            model='M2 Cusing',
            producer='ConceptLaser',
            url='http://www.conceptlaserinc.com/machines/'
        )
#end 'class FaustsonSample(pif.System):'

def file_kernel(ifile):
    # read CSV file
    csv = np.genfromtxt(ifile, delimiter=',', names=True, dtype=None)
    # get a list of column names
    names = csv.dtype.names
    # process samples
    samples = []
    for entry in csv:
        sample = FaustsonSample()
        for name in names:
            # the annealing step is not stored in the CSV, just whether
            # or not this sample was annealed/heat treated. This could
            # be extended trivially (though cryptically) by replacing the
            # boolean with a scalar, e.g. 0 = no anneal, 1 = inconel
            # 980 + 720 + 620, ...
            if name == 'annealed':
                if entry['annealed']:
                    sample.alloy.anneal(1253, 1, description='solution anneal')
                    sample.alloy.cool(1253, description='oven cool')
                    sample.alloy.anneal(993, 8, description='aging-1')
                    sample.alloy.cool(993, 2, Tstop=893, description='aging-2')
                    sample.alloy.anneal(893, 8, description='aging-3')
            else:
                # all other attributes are stored.
                setattr(sample, name, entry[name])
        samples.append(sample)
    print "Finished processing {} samples".format(len(samples))
    return samples
#end 'def file_kernel(ifile):'

def main ():
    global args
    samples = []
    # read each file
    for ifile in args.filelist:
        samples.extend(file_kernel(ifile))
    # write
    path, ofile = os.path.split(ifile)
    ofile, ext = os.path.splitext(ofile)
    ofile = '{}.pif'.format(ofile)
    with open(ofile, 'w') as ofs:
        for s in samples:
            ofs.write(str(s.as_pif_dictionary()))
#end 'def main ():'

if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = argparse.ArgumentParser(
                #prog='HELLOWORLD', # default: sys.argv[0], uncomment to customize
                description=textwrap.dedent(globals()['__doc__']),
                epilog=textwrap.dedent("""\
                    EXIT STATUS

                        0 on success

                    AUTHOR

                        Branden Kappes <bkappes@mines.edu>

                    LICENSE

                        This script is in the public domain, free from copyrights
                        or restrictions.
                        """))
        # positional parameters
        parser.add_argument('filelist',
            metavar='file',
            type=str,
            nargs='*', # if there are no other positional parameters
            #nargs=argparse.REMAINDER, # if there are
            help='Files to process.')
        # optional parameters
        parser.add_argument('-v',
            '--verbose',
            action='count',
            default=0,
            help='Verbose output')
        parser.add_argument('--version',
            action='version',
            version='%(prog)s 0.1')
        args = parser.parse_args()
        # check for correct number of positional parameters
        #if len(args.filelist) < 1:
            #parser.error('missing argument')
        # timing
        if args.verbose > 0: print time.asctime()
        main()
        if args.verbose > 0: print time.asctime()
        if args.verbose:
            delta_time = time.time() - start_time
            hh = int(delta_time/3600.); delta_time -= float(hh)*3600.
            mm = int(delta_time/60.); delta_time -= float(mm)*60.
            ss = delta_time
            print 'TOTAL TIME: {0:02d}:{1:02d}:{2:06.3f}'.format(hh,mm,ss)
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
#end 'if __name__ == '__main__':'
