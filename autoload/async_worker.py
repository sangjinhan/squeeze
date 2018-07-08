#!/usr/bin/env python3

import multiprocessing
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import traceback


class AsyncWorker(multiprocessing.Process):
    def __init__(self, out_q, path_src, path_script, args):
        super(AsyncWorker, self).__init__()
        self.out_q = out_q
        self.path_src = path_src
        self.path_script = path_script
        self.args = args

    def _do_run(self):
        args = shlex.split('{} {} {}'.format(self.path_script, self.path_src, 
                                             self.args))
        proc = subprocess.Popen(args, universal_newlines=True,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        self.out_q.put((out, err))

    def run(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            os.environ['TMPDIR'] = tmp_dir
            self._do_run()
        except:
            traceback.print_exc(file=sys.stderr)
        finally:
            shutil.rmtree(tmp_dir)
