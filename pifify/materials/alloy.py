import sys
sys.path.append('/Users/bkappes/src/citrine/pypif')
from copy import deepcopy
from pypif import pif

class AlloyBase(pif.Alloy):
    def __init__(self, **kwds):
        super(AlloyBase, self).__init__(**kwds)

    def _thermal(self, Tstart, duration, **kwds):
        """
        Specify an thermal step that runs from TSTART to TSTOP
        over DURATION.

        Parameters
        ----------
        :Tstart, (pif.Value, number): Start temperature of the thermal step.
        :duration, (pif.Value, number): Duration of the thermal step.

        Keywords
        --------
        :atmosphere, (pif.Value, str): atmosphere under which the thermal
            treatment occurs. Default: None
        :description, str: Description of the thermal step. Default: thermal
        :Tstop, (pif.Value, number): Stop temperature of the thermal step.
            Default: TSTART
        """
        # description of the process
        description = str(kwds.get('description', 'thermal'))
        descriptions = [p.name for p in self.preparation]
        if description in descriptions:
            base = description
            while description in descriptions:
                i = 1
                description = '{}-{:02d}'.format(base, i)
        # set the values
        details = []
        if 'atmosphere' in kwds:
            if isinstance(kwds['atmosphere'], str):
                atmosphere = pif.Property(name='atmosphere',
                                          condition='Ar')
                details.append(atmosphere)
        #
        if isinstance(duration, (int, float)):
            duration = pif.Value(name='duration',
                                 scalars=[pif.Scalar(duration)],
                                 units=['hr'])
        assert(isinstance(duration, pif.Value))
        details.append(duration)
        #
        if isinstance(Tstart, (int, float)):
            Tstart = pif.Value(name='Tstart',
                               scalars=[pif.Scalar(Tstart)],
                               units=['K'])
        assert(isinstance(Tstart, pif.Value))
        details.append(Tstart)
        #
        if 'Tstop' not in kwds:
            Tstop = deepcopy(Tstart)
            Tstop.name = 'Tstop'
        elif isinstance(kwds['Tstop'], (int, float)):
            Tstop = pif.Value(name='Tstop',
                               scalars=[pif.Scalar(kwds['Tstop'])],
                               units=['K'])
        else:
            Tstop = kwds['Tstop']
        assert(isinstance(Tstop, pif.Value))
        details.append(Tstop)
        # create the step
        prepstep = pif.ProcessStep()
        prepstep.name = description
        prepstep.details = details
        self.preparation.append(prepstep)
    def anneal(self, Tstart, duration, **kwds):
        if 'description' not in kwds:
            kwds['description'] = 'anneal'
        self._thermal(Tstart, duration, **kwds)
    def cool(self, Tstart, duration=24, **kwds):
        if 'Tstop' not in kwds:
            kwds['Tstop'] = 273
        if 'description' not in kwds:
            kwds['description'] = 'cool'
        self._thermal(Tstart, duration, **kwds)
#end 'class AlloyBase(pif.Alloy):'