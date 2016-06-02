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
import errno
import tarfile
import numpy as np
from hashlib import md5 as hashfunc
from uuid import UUID
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
    _prep = {}
    _props = {}

    def __new__(cls, name, parents, dct):
        dct['__getattr__'] = SampleMeta.getattr
        dct['__setattr__'] = SampleMeta.setattr
        dct['__contains__'] = SampleMeta.contains
        return super(SampleMeta, cls).__new__(cls, name, parents, dct)

    @staticmethod
    def attribute_generator(cls, name, rval):
        """Creates a new attribute for type CLS"""
        if not hasattr(cls, name):
            setattr(cls, name, lambda instance: rval)

    @staticmethod
    def contains(inst, key):
        cls = type(inst)
        return (key in cls._prep) or (key in cls._props)

    @staticmethod
    def getattr(inst, key):
        cls = type(inst)
        haskey = ((key in cls._prep) or \
                  (key in cls._props))
        if haskey and not hasattr(cls, key):
            return None
        return super(cls, inst).__getattr__(key)

    @staticmethod
    def setattr(inst, key, *args):
        cls = type(inst)
        # is the key in the preparation or properties dictionary?
        if key in cls._prep:
            dct = cls._prep
            if not isinstance(inst.printing.details, list):
                inst.printing.details = []
            dest = inst.printing.details
        elif key in cls._props:
            dct = cls._props
            if not isinstance(inst.properties, list):
                inst.properties = []
            dest = inst.properties
        else:
            dct = None
        if dct:
            # set the value
            value = dct[key](*args)
            # add the properties to the sample properties list
            dest.append(value)
            # store convenient access to this property
            # if more than one property is given the same name, then only
            # the most recent will retain programmatic access through the
            # attribute. However, both will be stored in the properties
            # field
            SampleMeta.attribute_generator(cls, key, value)
        else:
            attr = key
            value = args[0]
            super(cls, inst).__setattr__(attr, value)
#end 'class SampleMeta(type):'


def value_factory(name, **kwds):
    """
    Value factory

    Returns a function that accepts one or more scalar values and returns
    a named pif.Value object.

    Arguments
    ---------
    :name, str: Name of the value

    Keywords
    --------
    All keywords are passed into pif.Value.
    """
    kwds['name'] = name
    def func(x):
        kwds['scalars'] = x
        return pif.Value(**kwds)
    return func
# preparation_factory is nothing more than a value_factory whose return
# value is meant to be stored in a ProcessStep object
preparation_factory = value_factory


def property_factory(name, **kwds):
    """
    Property factory

    Returns a function that accepts one or more scalar values and returns
    a named pif.Property object.

    Arguments
    ---------
    :name, str: Name of the property

    Keywords
    --------
    All keywords are passed into pif.Property.
    """
    kwds['name'] = name
    def func(x):
        kwds['scalars'] = x
        return pif.Property(**kwds)
    return func


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
            preparation_factory('polar angle', units='degrees'),
        'powderSize' : lambda low, high : \
            pif.Property(name = 'powder size',
                         scalars = pif.Scalar(minimum=low, maximum=high),
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
            preparation_factory('azimuth angle', units='degrees'),
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


def csv_kernel(ifile):
    # Process a single CSV file. Eventually this will need to be modified
    # or renamed to be part-specific, e.g. Faustson samples vs. Lockheed
    # samples, etc.
    #
    # read CSV file
    csv = np.genfromtxt(ifile, delimiter=',', names=True, dtype=None)
    # get a list of column names
    names = csv.dtype.names
    # process samples
    samples = []
    for entry in csv:
        sample = FaustsonSample()
        for name in names:
            if name not in sample:
                msg = '{} is not a recognized field.'.format(name)
                raise AttributeError(msg)
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
                if name == 'plate':
                    num = int(entry[name])
                    if num in (1, 2, 3, 4):
                        setattr(sample, 'plateMaterial', 'P20 steel')
        samples.append(sample)
    #print "Finished processing {} samples".format(len(samples))
    return samples
#end 'def csv_kernel(ifile):'


def make_directory(name, retry=0):
    """
    Makes a directory named NAME. If this fails because the directory
    already exists and RETRY > 0, then use a counter to create a
    new directory that doesn't exist, up to RETRY times.
    """
    if retry > 0:
        counter = 0
        # zero pad the counter according to the max number of retries
        fmt = '{}-{:0%d}' % (int(np.log10(retry)) + 1)
    directory = name
    while True:
        try:
            os.mkdir(directory)
            return directory
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                # if error number is EACCES (permission denied), ENOSPC (no
                # space on device), or EROFS (read-only file system), then fail
                raise exc
            elif retry > 0:
                # error number is EEXIST (directory exists) and RETRY > 0
                counter += 1
                directory = fmt.format(name, counter)
                if counter >= retry:
                    msg = 'Exceeded the number of unique directory ' \
                          'names to try.'
                    raise IOError(msg)
            else:
                # error number is EEXIST and RETRY is False.
                raise exc


def main ():
    global args
    samples = []
    # ####################################
    # read
    # ####################################
    for ifile in args.filelist:
        samples.extend(csv_kernel(ifile))
    # ####################################
    # write
    # ####################################
    # To improve traceability of the samples and their history, each sample
    # should be uploaded separately, i.e. as a separate file. So rather than
    # storing these in a single file, create a directory -- whose name is based
    # on the input file, store each sample as a separate file in that
    # directory, then tar and zip the directory.
    path, basename = os.path.split(ifile)
    directory, junk = os.path.splitext(basename) # junk the extension
    directory = make_directory(directory, retry=0)
    ofiles = []
    for sample in samples:
        # generate JSON string
        jstr = pif.dumps(sample, indent=4)
        # hash the JSON string to create an URN
        urn = UUID(hashfunc(jstr).hexdigest()).get_urn()
        urn = urn.split(':')[-1]
        # store this in the newly created directory
        ofile = '{}/{}.json'.format(directory, urn)
        # check if this file already exists
        prev = [i for i,fname in enumerate(ofiles) if ofile == fname]
        if len(prev) > 0:
            curr = len(ofiles)+1
            msg = 'Sample {} and sample {} are identical.'.format(prev[0], curr)
            if not args.duplicate_error:
                sys.stdout.write('WARNING: {} ' \
                                 'Skipping sample {}.\n'.format(msg, curr))
                continue
            else:
                msg = '{} To skip duplicates, invoke the ' \
                      '--duplicate-warning flag.'.format(msg)
                shutil.rmtree(directory)
                raise IOError(msg)
        ofiles.append(ofile)
        # write the file
        with open(ofile, 'w') as ofs:
            ofs.write(jstr)
    # tarball and gzip the new directory
    tarball = '{}.tgz'.format(directory)
    with tarfile.open(tarball, 'w:gz') as tar:
        tar.add(directory)
    shutil.rmtree(directory)
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
        parser.add_argument('--duplicate-error',
            dest='duplicate_error',
            action='store_true',
            default=True,
            help='Stop processing if duplicate samples are found.')
        parser.add_argument('--duplicate-warning',
            dest='duplicate_error',
            action='store_false',
            help='Print a warning message and skip duplicate samples.')
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
        if len(args.filelist) < 1:
            parser.error('missing argument')
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
        sys.stderr.write('Caught keyboard interrupt.\n')
        sys.exit(1)
    except IOError, e:
        sys.stderr.write(e.message + '\n')
        sys.exit(1)
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
#end 'if __name__ == '__main__':'
