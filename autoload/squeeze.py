#!/usr/bin/env python3

import time
import multiprocessing
import os

import vim

from async_worker import AsyncWorker
import utils

# Global map for host (source code) window ID -> Squeezer instance
squeezers = {}

# set of Squeezer instances that are waiting for updates
polling_squeezers = set()


def create_window(buf_name):
    vim.command('rightbelow vnew {}'.format(buf_name))
    
    vim.command('let w:squeeze_args=""')

    # Use vim.command(), not buf.options[], since the options may not exist
    vim.command('setlocal nomodifiable')
    vim.command('setlocal buftype=nofile')
    vim.command('setlocal syntax=objdump')
    vim.command('setlocal filetype=squeeze')

    return vim.current.window


class Squeezer:
    BUFNAME_PREFIX = '__Squeeze__'

    def __init__(self, win):
        self.host_win = win
        self.host_winid = utils.win_to_winid(win)
        self.host_buf = win.buffer
        self.host_bufnr = win.buffer.number

        guest_buf_name = '{}.{}.{}'.format(self.BUFNAME_PREFIX,
                                           self.host_winid,
                                           self.host_buf.name)

        self.guest_win = create_window(guest_buf_name)
        self.guest_winid = utils.win_to_winid(self.guest_win)
        self.guest_buf = self.guest_win.buffer
        self.guest_bufnr = self.guest_buf.number

        self._add_autocmd('BufWritePost', self.host_bufnr,
                          'trigger_build({})'.format(self.host_winid))
        self._add_autocmd('QuitPre', self.host_bufnr,
                          'cleanup_squeezer({})'.format(self.host_winid))
        self._add_autocmd('BufUnload', self.guest_bufnr,
                          'cleanup_squeezer({})'.format(self.host_winid))

        # focus back to the host window
        vim.current.window = self.host_win
        utils.log('object created for {}({})'.format(
            win.buffer.name, win.number))

        self.worker = None
        self.async_build()

    def __del__(self):
        if self.host_winid in squeezers:
            squeezers.pop(self.host_winid)

        if self in polling_squeezers:
            polling_squeezers.remove(self)

    def _add_autocmd(self, ev, bufnr, py_stmt):
        cmd = 'call s:Python("{}")'.format(py_stmt)
        vim.command('augroup SqueezeAutoCmds{}'.format(self.host_winid))
        vim.command('  autocmd {} <buffer={}> {}'.format(ev, bufnr, cmd))
        vim.command('augroup END')

    def _del_autocmd(self, ev, bufnr):
        vim.command('augroup SqueezeAutoCmds{}'.format(self.host_winid))
        vim.command('  autocmd! {} <buffer={}>'.format(ev, bufnr))
        vim.command('augroup END')

    # Close the guest window and destroy the outstanding worker
    def cleanup(self):
        if self.worker:
            self.worker.terminate()
            self.worker.join()
            self.worker = None

        if self.host_winid in squeezers:
            squeezers.pop(self.host_winid)

        if self.guest_win.valid:
            vim.command('{}close'.format(self.guest_win.number))

        self._del_autocmd('*', self.host_bufnr)
        self._del_autocmd('*', self.guest_bufnr)

        utils.log('object destroyed for {}({})'.format(self.host_buf.name,
                                                       self.host_winid))

    def async_build(self):
        if self.worker:
            utils.log('killing existing thread')
            self.worker.terminate()
            self.worker.join()

        script = utils.get_var('squeeze_c_script')
        args = utils.get_var('squeeze_c_args')

        if args:
            self.guest_win.vars['squeeze_args'] = args
        else:
            self.guest_win.vars['squeeze_args'] = '<none>'

        path_script = os.path.join(vim.eval('s:plugin_path'), 'scripts/',
                                   script, 'objdump')
        self.out_q = multiprocessing.Queue()
        self.worker = AsyncWorker(self.out_q, self.host_win.buffer.name,
                                  path_script, args)
        self.worker.start()

        if len(polling_squeezers) == 0:
            vim.command('''
                let g:squeeze_timer = timer_start(100, \
                        function('s:TimerHandler'), {'repeat': -1})
            ''')
        else:
            vim.command('call timer_pause(g:squeeze_timer, 0)')

        polling_squeezers.add(self)

    def update_result(self):
        if not self.guest_win.valid:
            self.cleanup()
            return

        if self.worker and not self.out_q.empty():
            out, err = self.out_q.get()
            output = out + '\n-------\n' + err

            self.worker.join()
            exit_code = self.worker.exitcode

            self.worker = None

            # temporarily make the buffer modifiable
            self.guest_buf.options['modifiable'] = 1
            self.guest_buf[:] = output.split('\n')
            self.guest_buf.options['modifiable'] = 0

            if self in polling_squeezers:
                polling_squeezers.remove(self)


def _toggle_on(win):
    obj = Squeezer(win)
    squeezers[obj.host_winid] = obj


def _toggle_off(win):
    squeezers[utils.win_to_winid(win)].cleanup()


def toggle():
    win = vim.current.window
    winid = utils.win_to_winid(win)

    if winid in squeezers:
        _toggle_off(win)
    else:
        # Toggle hit in a guest window?
        for obj in list(squeezers.values()):
            if obj.guest_winid == winid:
                _toggle_off(obj.host_win)
                return

        # Is is a regular file?
        opts = win.buffer.options
        if 'buftype' in opts and opts['buftype'] not in ['', b'']:
            vim.command('echohl WarningMsg')
            vim.command('echomsg "Not a regular file"')
            vim.command('echohl None')
        else:
            _toggle_on(win)


def trigger_build(host_winid):
    if host_winid in squeezers:
        squeezers[host_winid].async_build()


def cleanup_squeezer(host_winid):
    if host_winid in squeezers:
        squeezers[host_winid].cleanup()


def poll_result():
    for obj in list(polling_squeezers):
        obj.update_result()

    if len(polling_squeezers) == 0:
        vim.command('call timer_pause(g:squeeze_timer, 1)')
