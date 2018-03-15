"""
printing.py - printing classes for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
NOTE: Parts of this file are based on code from Stef Mientki
<https://groups.google.com/forum/?fromgroups=#!msg/wxpython-users/cl0fY0jH5lk/cefRP6qyJHYJ>
"""

import os.path
import time
import wx

_ = wx.GetTranslation

class Printout(wx.Printout):
	def __init__(self, editor, margins):
		wx.Printout.__init__(self, editor.filename)
		self._editor = editor
		
		self.font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
		self.margins = margins
		self.offsets = []
		self.pages = 0
	
	def HasPage(self, page):
		return page <= self.pages
	
	def GetPageInfo(self):
		return (1, self.pages, 1, self.pages)
	
	def CalculateScale(self, dc):
		ppi = self.GetPPIPrinter()[1]
		scale = 1.0 * ppi / self.GetPPIScreen()[1]
		width, height = dc.GetSize()
		scale2 = scale * height / self.GetPageSizePixels()[1]
		dc.SetUserScale(scale2, scale2)
		mm = 1.0 * ppi / (scale * 25.4)
		self.x1 = self.margins[0].x * mm
		self.y1 = self.margins[0].y * mm
		self.x2 = dc.DeviceToLogicalXRel(width) - self.margins[1].x * mm
		self.y2 = dc.DeviceToLogicalYRel(height) - self.margins[1].y * mm
		dc.SetFont(self.font)
		self.yoffset = dc.GetCharHeight() + 1
	
	def OnPreparePrinting(self):
		dc = self.GetDC()
		self.CalculateScale(dc)
		end = 0
		length = self._editor.GetTextLength()
		rect = wx.Rect(self.x1, self.y1 + self.yoffset + 1, self.x2 - self.x1, self.y2 - self.y1 - self.yoffset * 2 - 2)
		while end < length:
			start = end
			end = self._editor.FormatRange(False, start, length, dc, dc, rect, rect)
			self.offsets.append((start, end))
		self.pages = len(self.offsets)
		split = os.path.split(self._editor.filename)
		if self._editor._parent.editors[0].new:	# Don't show empty parentheses in the header
			self.filename = split[1]
		else:
			self.filename = "%s (%s)" % (split[1], split[0])
		dc.SetFont(self.font)
		i = len(self.filename)
		while dc.GetTextExtent(self.filename)[0] > self.x2 - self.x1 and i > 0:
			self.filename = "%s..." % self.filename[:i]
			i -= 1
		self.datetime = time.strftime("%c")
	
	def OnPrintPage(self, page):
		dc = self.GetDC()
		self.CalculateScale(dc)
		start, end = self.offsets[page - 1]
		rect = wx.Rect(self.x1, self.y1 + self.yoffset + 1, self.x2 - self.x1, self.y2 - self.y1 - self.yoffset * 2 - 2)
		self._editor.FormatRange(True, start, end, dc, dc, rect, rect)
		dc.SetFont(self.font)
		dc.SetTextForeground(wx.BLACK)
		dc.DrawText(self.filename, self.x1, self.y1)
		dc.DrawText(self.datetime, self.x1, self.y2 - self.yoffset + 2)
		pagenum = _("%d of %d") % (page, self.pages)
		dc.DrawText(pagenum, self.x2 - dc.GetTextExtent(pagenum)[0], self.y2 - self.yoffset + 2)
		dc.SetPen(wx.BLACK_PEN)
		dc.SetBrush(wx.TRANSPARENT_BRUSH)
		dc.DrawLine(self.x1, self.y1 + self.yoffset, self.x2 + 1, self.y1 + self.yoffset)
		dc.DrawLine(self.x1, self.y2 - self.yoffset, self.x2 + 1, self.y2 - self.yoffset)
		return True

class Printer:
	def __init__(self, app):
		self._app = app
		
		self.pdata = wx.PrintData()
		self.pdata.SetPaperId(wx.PAPER_LETTER)
		self.pdata.SetOrientation(wx.PORTRAIT)
		self.margins = (wx.Point(15, 15), wx.Point(15, 15))
	
	def Print(self, editor):
		data = wx.PrintDialogData(self.pdata)
		printer = wx.Printer(data)
		printout = Printout(editor, self.margins)
		printed = printer.Print(editor._frame, printout)
		if printed:
			self.pdata = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
		elif printer.GetLastError() == wx.PRINTER_ERROR:
			wx.MessageBox(_("'%s' could not be printed.\nMake sure that your printer is connected properly.") % editor.filename, _("Print"), wx.ICON_ERROR | wx.OK)
		printout.Destroy()
	
	def PageSetup(self):
		data = wx.PageSetupDialogData(self.pdata)
		data.SetPrintData(self.pdata)
		data.SetDefaultMinMargins(True)
		data.SetMarginTopLeft(self.margins[0])
		data.SetMarginBottomRight(self.margins[1])
		dialog = wx.PageSetupDialog(self._app.frames[self._app.active], data)
		if dialog.ShowModal() == wx.ID_OK:
			data = dialog.GetPageSetupData()
			self.pdata = wx.PrintData(data.GetPrintData())
			self.margins = (data.GetMarginTopLeft(), data.GetMarginBottomRight())
		dialog.Destroy()
	
	def Preview(self, editor):
		printout1 = Printout(editor, self.margins)
		printout2 = Printout(editor, self.margins)
		preview = wx.PrintPreview(printout1, printout2, self.pdata)
		preview.SetZoom(100)
		if preview.IsOk():
			frame = wx.PreviewFrame(preview, editor._frame, _("Print Preview (%s) - Write++") % os.path.split(editor.filename)[1], editor._frame.rect.GetPosition(), editor._frame.rect.GetSize())
			frame.Initialize()
			frame.Show()
		else:
			wx.MessageBox(_("'%s' cannot be previewed.\nMake sure that you have a print driver installed.") % editor.filename, _("Print Preview"), wx.ICON_ERROR | wx.OK)