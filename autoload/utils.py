#!/usr/bin/env python3

import time
import traceback

import vim


def log(msg):
    tb = traceback.extract_stack()
    print('{} {}: {}'.format(time.asctime(),
                             ' > '.join([func for _, _, func, _ in tb[1:-1]]),
                             msg))


def win_to_winid(win):
    # I am assuming winid is always an integer
    return int(vim.eval('win_getid({})'.format(win.number)))


# read a variable in the order of window, buffer, and global scopes
def get_var(var, default=''):
    try:
        return vim.eval('w:{}'.format(var))
    except vim.error:
        pass

    try:
        return vim.eval('b:{}'.format(var))
    except vim.error:
        pass

    try:
        return vim.eval('g:{}'.format(var))
    except vim.error:
        pass

    return default
