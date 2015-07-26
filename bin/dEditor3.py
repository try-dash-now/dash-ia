# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/7/26 
'''
#-*-coding:utf-8

#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      ankier
#
# Created:     14/10/2012
# Copyright:   (c) ankier 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import wx, wx.grid as grd

#定购的Grid cell ComboBox editor
class GridCellComboBoxEditor(grd.PyGridCellEditor):
    def __init__(self, choices = []):
        grd.PyGridCellEditor.__init__(self)
        self.__Choices = choices

    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        *Must Override*
        """
        self.__Parent = parent
        self.__ComboBoxDialog = None
        self.__ComboBoxButton = wx.ComboBox(parent, id, value = "", choices =self.__Choices)
        self.__ComboBoxButton.SetEditable(False)
        self.SetControl(self.__ComboBoxButton)
        #添加新的event handler， 防止 弹出窗口后， cell 自动editor
        newEventHandler = wx._core.EvtHandler()
        if evtHandler:
            self.__ComboBoxButton.PushEventHandler(newEventHandler)
        self.__ComboBoxButton.Bind(wx.EVT_COMBOBOX, self.OnClick)


    def OnClick(self, event):
        self.endValue = self.__ComboBoxButton.GetStringSelection()


    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self.__ComboBoxButton.SetDimensions(rect.x,rect.y,rect.width+2,rect.height+2,wx.SIZE_ALLOW_MINUS_ONE)

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellComboBoxEditor()

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing. Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        self.endValue = self.startValue
        self.__ComboBoxButton.SetStringSelection(self.startValue)

    def EndEdit(self, row, col, grid):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed. If necessary, the control may be destroyed.
        *Must Override*
        """
        changed = False
        if self.endValue != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, self.endValue) # update the table
            self.startValue = ''
        return changed



#定购颜色cell colour column
class GridCellComboBoxRender(grd.GridCellStringRenderer):
    def __init__(self):
        grd.GridCellStringRenderer.__init__(self)