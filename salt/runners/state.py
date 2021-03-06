# -*- coding: utf-8 -*-
'''
Execute overstate functions
'''

# Import pytohn libs
from __future__ import print_function

# Import salt libs
import salt.output
import salt.overstate
from salt.exceptions import SaltInvocationError


def over(saltenv='base', os_fn=None):
    '''
    .. versionadded:: 0.11.0

    Execute an overstate sequence to orchestrate the executing of states
    over a group of systems

    CLI Examples:

    .. code-block:: bash

        salt-run state.over base /path/to/myoverstate.sls
    '''
    stage_num = 0
    try:
        overstate = salt.overstate.OverState(__opts__, saltenv, os_fn)
    except IOError as exc:
        raise SaltInvocationError(
            '{0}: {1!r}'.format(exc.strerror, exc.filename)
        )
    for stage in overstate.stages_iter():
        if isinstance(stage, dict):
            # This is highstate data
            print('Stage execution results:')
            for key, val in stage.items():
                if '_|-' in key:
                    salt.output.display_output(
                            {'error': {key: val}},
                            'highstate',
                            opts=__opts__)
                else:
                    salt.output.display_output(
                            {key: val},
                            'highstate',
                            opts=__opts__)
        elif isinstance(stage, list):
            # This is a stage
            if stage_num == 0:
                print('Executing the following Over State:')
            else:
                print('Executed Stage:')
            salt.output.display_output(stage, 'overstatestage', opts=__opts__)
            stage_num += 1
    return overstate.over_run


def orchestrate(mods, saltenv='base', test=None, exclude=None, pillar=None):
    '''
    .. versionadded:: 0.17.0

    Execute a state run from the master, used as a powerful orchestration
    system.

    CLI Examples:

    .. code-block:: bash

        salt-run state.orchestrate webserver
        salt-run state.orchestrate webserver saltenv=dev test=True

    .. versionchanged:: 2014.1.1

        Runner renamed from ``state.sls`` to ``state.orchestrate``
    '''
    if pillar is not None and not isinstance(pillar, dict):
        raise SaltInvocationError(
            'Pillar data must be formatted as a dictionary'
        )
    __opts__['file_client'] = 'local'
    minion = salt.minion.MasterMinion(__opts__)
    running = minion.functions['state.sls'](mods, saltenv, test, exclude)
    ret = {minion.opts['id']: running}
    salt.output.display_output(ret, 'highstate', opts=__opts__)
    return ret

# Aliases for orchestrate runner
orch = orchestrate
sls = orchestrate


def show_stages(saltenv='base', os_fn=None):
    '''
    .. versionadded:: 0.11.0

    Display the OverState's stage data

    CLI Examples:

    .. code-block:: bash

        salt-run state.show_stages
        salt-run state.show_stages saltenv=dev /root/overstate.sls
    '''
    overstate = salt.overstate.OverState(__opts__, saltenv, os_fn)
    salt.output.display_output(
            overstate.over,
            'overstatestage',
            opts=__opts__)
    return overstate.over
