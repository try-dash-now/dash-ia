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

#grid column类型
class GridColumnControlKind:
    Text ="Text"
    CheckBox = "CheckBox"
    Colour = "Colour"

#定购的Grid cell color editor
class GridCellColorEditor(grd.PyGridCellEditor):
    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        *Must Override*
        """
        self.__Parent = parent
        self.__ColorDialog = None
        self.__ColorButton = wx.Button(parent, id, "")
        self.SetControl(self.__ColorButton)
        #添加新的event handler， 防止 弹出窗口后， cell 自动editor
        newEventHandler = wx._core.EvtHandler()
        if evtHandler:
            self.__ColorButton.PushEventHandler(newEventHandler)
        self.__ColorButton.Bind(wx.EVT_BUTTON, self.OnClick)


    def OnClick(self, event):
        self.__ColorButton.SetFocus()
        self.ShowColorDialog()

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self.__ColorButton.SetDimensions(rect.x,rect.y,rect.width+2,rect.height+2,wx.SIZE_ALLOW_MINUS_ONE)

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return GridCellColorEditor()

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing. Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        self.endValue = self.startValue
        self.__ColorButton.SetBackgroundColour(self.startValue)

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

    def ShowColorDialog(self):
        colorDialog = wx.ColourDialog(self.__Parent)
        self.__ColorDialog = colorDialog
        colorDialog.GetColourData().SetColour(self.startValue)
        if wx.ID_OK == colorDialog.ShowModal():
            data = colorDialog.GetColourData()
            colour = data.GetColour()
            self.__ColorButton.SetBackgroundColour(colour)
            self.endValue = colour

        del self.__ColorDialog
        self.__ColorDialog = None

#定购颜色cell colour column
class GridCellColorRender(grd.PyGridCellRenderer):
    def __init__(self):
        grd.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        color = grid.GetTable().GetValue(row, col)
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)

        dc.SetBackgroundMode(wx.TRANSPARENT)
    def GetBestSize(self, grid, attr, dc, row, col):
#        text = grid.GetCellValue(row, col)
#        dc.SetFont(attr.GetFont())
#        w, h = dc.GetTextExtent(text)
        return wx.Size(-1, -1)

    def Clone(self):
        return GridCellColorRender()

#根据具体业务逻辑 定购grid的 table
class CustomGridTable(grd.PyGridTableBase):
    def __init__(self):
        grd.PyGridTableBase.__init__(self)

        #添加Grid column head
        self.colLabels = ["Name", "Visibility", "Min threshold", "Max threshold", "Colour"]
        #指定column对应的kind control
        self.colControlKinds = [GridColumnControlKind.Text, GridColumnControlKind.CheckBox, GridColumnControlKind.Text, GridColumnControlKind.Text, GridColumnControlKind.Colour]
        self.colControlEditorEnableStatus =[True, True, False, False, True]
        self.rowLabels = ["","","","",""]

        #添加数据源
        self.Data = [
        ['Mask 1', 1, "2.5","320.6",(200,20,100)]
        ,['Mask 2', 1, "2.5","320.6",(50,0,200)]
        ]

    def GetNumberRows(self):
        return len(self.Data)

    def GetNumberCols(self):
        return len(self.colLabels)

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.Data[row][col]

    def SetValue(self, row, col, value):
        self.Data[row][col] = value

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetRowLabelValue(self, row):
        return self.rowLabels[row]

    def InsertRow(self, index, row):
        if len(self.Data) < index:
            return

        self.Data.insert(index, row)
        print self.Data
        self.GetView().BeginBatch()

        msg = grd.GridTableMessage(self,
                        grd.GRIDTABLE_NOTIFY_ROWS_INSERTED
                        ,index
                        ,1
                        )
        self.GetView().ProcessTableMessage(msg)

        # ... same thing for columns ....

        self.GetView().EndBatch()
        msg = grd.GridTableMessage(self, grd.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)

    def DeleteRow(self, row):
        rowIndex = self.Data.index(row )
        if rowIndex <0:
            return

        self.Data.remove(row)

        self.GetView().BeginBatch()

        msg = grd.GridTableMessage(self,grd.GRIDTABLE_NOTIFY_ROWS_DELETED,
                                   rowIndex,
)
        self.GetView().ProcessTableMessage(msg)

        # ... same thing for columns ....

        self.GetView().EndBatch()
        msg = grd.GridTableMessage(self, grd.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)

    def Clear(self):

        self.GetView().BeginBatch()

        msg = grd.GridTableMessage(self,grd.GRIDTABLE_NOTIFY_ROWS_DELETED,
                                    0,
                                   self.GetNumberCols()-1)
        self.GetView().ProcessTableMessage(msg)

        # ... same thing for columns ....

        self.GetView().EndBatch()

        self.Data = []

        msg = grd.GridTableMessage(self, grd.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)

    def AppendRow(self, row):
        self.Data.append(row)
        self.GetView().BeginBatch()

        msg = grd.GridTableMessage(self,
                        grd.GRIDTABLE_NOTIFY_ROWS_APPENDED,

                        )
        self.GetView().ProcessTableMessage(msg)

        # ... same thing for columns ....

        self.GetView().EndBatch()
        msg = grd.GridTableMessage(self, grd.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)



#对grid的功能进行封装 以便能方便的处理
class CustomGrid(grd.Grid):
    def __init__(self, parent, id, rowLabelSize = 0, customGridTable = None):
        grd.Grid.__init__(self, parent,id)

        self.RowLabelSize = rowLabelSize
        self.__CustomTableSource = customGridTable
        self.SetTable(self.__CustomTableSource, True)

        self.__InitStyle()

        #设置column 对应的 editor
        self.__InitColumnsEditor()

        # self.Bind(grd.EVT_GRID_CELL_LEFT_CLICK,self.__OnMouse)
        self.Bind(grd.EVT_GRID_SELECT_CELL, self.__OnCellSelected)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.__OnEditorCreated)

    def __InitStyle(self):
        self.SetSelectionBackground(wx.Colour(237  , 145  ,  33    ))

    def __InitColumnsEditor(self):
        index = -1
        for columnKind in self.__CustomTableSource.colControlKinds:
            index += 1
            if columnKind == GridColumnControlKind.CheckBox:
                self.__InitCheckBoxColumnEditor(index)
            elif columnKind == GridColumnControlKind.Colour:
                self.__InitColorColumnEditor(index)


    def __InitCheckBoxColumnEditor(self, columnIndex):
        attr = grd.GridCellAttr()
        attr.SetEditor(grd.GridCellBoolEditor())
        attr.SetRenderer(grd.GridCellBoolRenderer())
        self.SetColAttr(columnIndex, attr)

    def __InitColorColumnEditor(self, columnIndex):
        attr = grd.GridCellAttr()
        attr.SetEditor(GridCellColorEditor())
        attr.SetRenderer(GridCellColorRender())
        self.SetColAttr(columnIndex, attr)


    def __OnCellSelected(self,evt):
        if self.__CustomTableSource.colControlEditorEnableStatus[evt.Col]:
            wx.CallAfter(self.EnableCellEditControl)
            evt.Skip()
        #设置改行为选中状态
        self.SelectRow(evt.Row)

    def __OnEditorCreated(self, event):
        pass

    def ForceRefresh(self):
            grd.Grid.ForceRefresh(self)

#主窗口
class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None,title="GridTable",size=(500,200))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        addButton = wx.Button(self, -1, "Add")
        deleteButton = wx.Button(self, -1, "Delete")
        clearButton = wx.Button(self, -1, "Clear")
        sizer.Add(addButton, 0, wx.SHAPED)
        sizer.Add(deleteButton, 0, wx.SHAPED)
        sizer.Add(clearButton, 0, wx.SHAPED)

        table = CustomGridTable()
        grid = CustomGrid(self, id = -1, customGridTable = table)
        self.__Grid = grid
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer)
        mainSizer.Add(grid, 1, wx.EXPAND)
        self.SetSizerAndFit(mainSizer)

        addButton.Bind(wx.EVT_BUTTON, self.OnAddClick)
        deleteButton.Bind(wx.EVT_BUTTON, self.OnDeleteClick)
        clearButton.Bind(wx.EVT_BUTTON, self.OnClearClick)

    def OnClearClick(self, event):
        table  = self.__Grid.GetTable()
        table.Clear()
        print self.__Grid.GetTable().Data

    def OnDeleteClick(self, event):
        table  = self.__Grid.GetTable()
        firstRow = table.Data[1]
        table.DeleteRow(firstRow)
        print self.__Grid.GetTable().Data

    def OnAddClick(self, event):
        table  = self.__Grid.GetTable()
        table.InsertRow(1, ['insert index ', 1, "2.5","110.6",(50,200,30)])
        print self.__Grid.GetTable().Data


def main():
    app = wx.PySimpleApp()
    frame = TestFrame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()