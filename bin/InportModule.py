__author__ = 'Sean Yu'
'''created @2015/7/2'''
from  Tkinter import Tk,Tcl
import os
class tcltk(Tkinter.Tk):
    def __init__(self):
        Tkinter.Tk.__init__(self, None, None, 'Tk', 0)
tcltk()
from baseSession import baseSession
a =baseSession('base', {})