#!/usr/bin/python2.6

"""
Call this like ``python lavaflow-venv.py``; it will
refresh the lavaflow-bootstrap.py script

crib https://github.com/socialplanning/fassembler/blob/master/fassembler/create-venv-script.py
"""
import os
import subprocess
import re
from optparse import OptionParser
import virtualenv

EXTRA_TEXT = """

import pwd
import sys

LAVAFLOW_DIST_LOCATION='https://github.com/irvined1982/lavaflow.git'
LAVAFLOW_DIST_BRANCH='main'

def extend_parser(parser):
    parser.add_option(
        '--lavaflow-dist',
        dest='lavaflow_dist',
        default=LAVAFLOW_DIST_LOCATION,
        help='Location of a repository to use for the installation of lavaflow-dist')
    parser.add_option(
        '--dist-branch',
        dest='lavaflow_dist_branch',
        default=LAVAFLOW_DIST_BRANCH,
        help='Branch name of repository to use for the installation of lavaflow-dist')

def adjust_options(options, args):
    if not args:
        return # caller will raise error
    # We're actually going to build the venv in a subdirectory
    base_dir = args[0]
    args[0]  = join(base_dir, 'lavaflow-env')

def after_install(options, home_dir):
    base     = os.path.abspath(os.path.dirname(home_dir))
    lavaflow = os.path.join(base, 'lavaflow')
    activate = os.path.join(home_dir, 'bin', 'activate')
    post_act = os.path.join(home_dir, 'bin', 'post_activate')
    
    logger.notify('Updating activate script for loading of post_activate')
    f = open(activate, 'a')
    f.write('## load post_activate script if exists...\\n')
    f.write('[ -f $VIRTUAL_ENV/bin/post_activate ] && source $VIRTUAL_ENV/bin/post_activate\\n')
    f.write('## done with additions\\n')
    f.close()

    logger.notify('Writing LAVAFLOW_ROOT to post_activate script')
    f = open(post_act, 'w')
    f.write('## set LAVAFLOW_ROOT\\n')
    f.write(''.join(['export LAVAFLOW_ROOT', '=', lavaflow, '\\n']))
    f.write('## done with additions\\n')
    f.close()

    logger.notify('Pulling required repositories')
    logger.indent += 2
    try:
        if not os.path.isdir(os.path.abspath(lavaflow)):
            call_subprocess(['git', 'clone', options.lavaflow_dist, 'lavaflow'],
                            cwd=base)
    except:
        assert False, 'ERROR'
    finally:
        logger.indent -= 2

    if options.lavaflow_dist_branch:
        logger.notify('Updating & Switching to branch "' + options.lavaflow_dist_branch + '"')
        try:
            call_subprocess(['git', 'checkout', options.lavaflow_dist_branch ],
                            cwd=os.path.abspath(lavaflow))
	    call_subprocess(['git', 'pull', 'origin', options.lavaflow_dist_branch ],
                            cwd=os.path.abspath(lavaflow))
        except:
            logger.notify('git checkout failed')

    ## TODO:
    ## possibly add symlinks to local_settings.py or settings.py from a private repository...
    
    activate_this = os.path.join(home_dir, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    logger.notify('Installing Django et al.');
    logger.indent += 2
    try:
        call_subprocess([os.path.abspath(join(home_dir, 'bin', 'pip')), 'install', 'Django'],
                        cwd=base)
        call_subprocess([os.path.abspath(join(home_dir, 'bin', 'pip')), 'install', 'MySQL-python'],
                        cwd=base)
    finally:
        logger.indent -= 2

"""

here        = os.path.dirname(os.path.abspath(__file__))
base_dir    = os.path.dirname(here)

def main():
    parser = OptionParser()
    parser.add_option('--prefix',
                      dest='prefix',
                      default=here,
                      help='prefix for the location of the resulting script')
    text   = virtualenv.create_bootstrap_script(EXTRA_TEXT, python_version='2.4')

    (options, args) = parser.parse_args()

    script_name = os.path.join(options.prefix, 'lavaflow-bootstrap.py')

    if os.path.exists(script_name):
        f = open(script_name)
        cur_text = f.read()
        f.close()
    else:
        cur_text = ''
        
    print 'Updating %s' % script_name
    if cur_text == 'text':
        print 'No update'
    else:
        print 'Script changed; updating...'
    f = open(script_name, 'w')
    f.write(text)
    f.close()


if __name__ == '__main__':
    main()
