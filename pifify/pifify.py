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
import textwrap, traceback, argparse, re
import time
import shutil
import errno
import tarfile
import numpy as np
from hashlib import md5 as hashfunc
from uuid import UUID
from pypif import pif
from pifify.io.input.Faustson import (P001B001,
                                      P002B001,
                                      P003B001,
                                      P004B001,
                                      P005B001,
                                      P005B002,
                                      P006B001)


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


def get_urn(key):
    """Generate a unique identifier from the key."""
    urn = UUID(hashfunc(key).hexdigest()).get_urn()
    urn = urn.split(':')[-1]
    return urn


def filename_from(key, directory='.', overwrite=False):
    """
    Makes a filename based on the hash of KEY.

    Parameters
    ----------
    :key, str: String object on which to construct a UUID-based filename.

    Keywords
    --------
    :directory, str: Directory in which to place the newly created file.
        Default: '.'
    :overwrite, bool: If True, then the existing file will be overwritten.
        If False (default), then an error is raised.

    Return
    ------
    The filename as a string.
    """
    # validate input
    directory=directory.rstrip('/')
    # hash the key to create a URN
    urn = get_urn(key)
    # store this in the newly created directory
    ofile = '{}/{}.json'.format(directory, urn)
    try:
        _ = open(ofile)
        if not overwrite:
            raise ValueError()
    except IOError:
        pass
    except ValueError:
        raise IOError()
    return ofile


def main ():
    global args
    samples = []
    # ####################################
    # read
    # ####################################
    for source in args.sources:
        try:
            subset = {
                'faustson-plate1-build1' : P001B001().samples,
                'faustson-plate2-build1' : P002B001().samples,
                'faustson-plate3-build1' : P003B001().samples,
                'faustson-plate4-build1' : P004B001().samples,
                'faustson-plate5-build1' : P005B001().samples,
                'faustson-plate5-build2' : P005B002().samples,
                'faustson-plate6-build1' : P006B001().samples
            }[source.lower()]
        except KeyError:
            raise ValueError('{source:} is not a recognized source.'.format(
                source=source))
        samples.extend(subset)
    # ####################################
    # write
    # ####################################
    # To improve traceability of the samples and their history, each sample
    # should be uploaded separately, i.e. as a separate file. So rather than
    # storing these in a single file, create a directory to store each sample
    # as a separate file in that directory, then tar and zip the directory.
    directory = args.output
    directory = make_directory(directory, retry=0)
    for sample in samples:
        # generate JSON string
        jstr = pif.dumps(sample, indent=4)
        # create a filename from the contents of the record
        try:
            ofile = filename_from(jstr, directory=directory)
        except IOError:
            msg = 'Sample {} is duplicated.'.format(ofile)
            if not args.duplicate_error:
                sys.stdout.write('WARNING: {}' \
                                 'Skipping.\n'.format(msg))
                continue
            else:
                msg = 'ERROR: {} To skip duplicates, invoke the ' \
                      '--duplicate-warning flag.'.format(msg)
                shutil.rmtree(directory)
                raise IOError(msg)
        # Add the UID to the record
        urn = get_urn(jstr)
        sample.uid = urn
        # write the file
        with open(ofile, 'w') as ofs:
            pif.dump(sample, ofs)
    # tarball and gzip the new directory
    if args.create_archive:
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
        parser.add_argument('sources',
            type=str,
            nargs='*', # if there are no other positional parameters
            #nargs=argparse.REMAINDER, # if there are
            help='List of what should be processed. Recognized keywords: ' \
                 'faustson-plate1-build1, faustson-plate2-build1, ' \
                 'faustson-plate3-build1, faustson-plate4-build1, ' \
                 'faustson-plate5-build1, faustson-plate5-build2, ' \
                 'faustson-plate6-build1.')
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
        parser.add_argument('-o',
            '--output',
            default='samples',
            help='Specify the output directory to hold the resulting files.')
        parser.add_argument('-v',
            '--verbose',
            action='count',
            default=0,
            help='Verbose output')
        parser.add_argument('--version',
            action='version',
            version='%(prog)s 0.1')
        parser.add_argument('-z',
            '--tgz',
            dest='create_archive',
            action='store_true',
            default=False,
            help='Create an archive of the resulting records using tar/gzip.')
        args = parser.parse_args()
        # check for correct number of positional parameters
        if len(args.sources) < 1:
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
