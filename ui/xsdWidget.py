'''
Created on Feb 21, 2013

@author = Santiago Diaz - salchoman@gmail.com
'''

from core.fwCore import core
from ui.IWidget import IWidget
import gtk

class xsdWidget(IWidget):
	def __init__(self):
		IWidget.__init__(self)
		self.vbox = None
		self.oCombobox = None
		self.wsdl = None
		self.selected_op = None
		self.sw = None
		
	def start(self):
		self.vbox = gtk.VBox()
		frame = gtk.Frame('Methods')
		frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.oCombobox = gtk.combo_box_new_text()
		self.oCombobox.append_text('')
		self.wsdl = core.iswsdlhelper()
		if self.wsdl:
			for op in self.wsdl.getMethods():
				self.oCombobox.append_text(op)
				self.oCombobox.connect('changed', self.changeOp)
			frame.add(self.oCombobox)
		self.vbox.pack_start(frame, False, False, 0)

	def getWidget(self):
		return self.vbox
	
	def changeOp(self, w):
		model = w.get_model()
		index = w.get_active()
		if index:
			op = model[index][0]
			if op != self.selected_op or self.selected_op == '':
				self.selected_op = op
				self.renderInfo()
			
	def renderInfo(self):
		if self.sw:
			self.sw.destroy()
		self.sw = gtk.ScrolledWindow()
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		frame = gtk.Frame("Properties")
		params = self.wsdl.getParamsSchema(self.selected_op)
		if params and len(params) > 0:
			table = fwTable(self.wsdl.getParamsSchema(self.selected_op), self.wsdl.getParamsNames(self.selected_op))
			frame.add(table.getWidget())
		else:
			frame.add(gtk.Label("This method has no parameters!"))
		self.sw.add_with_viewport(frame)
		self.sw.show_all()
		self.vbox.pack_start(self.sw, True, True, 0)
		self.vbox.show_all()	
						
class fwTable(IWidget):
	def __init__(self, schemas, names):
		rows = 0
		for s in schemas:
			if s.children() != []:
				rows += len(s.children())
			else:
				rows += 1
		
		self.table = gtk.Table(rows + 1, 6, True)
		self.table.attach(gtk.Label("Type "), 1, 2, 0, 1 )
		self.table.attach(gtk.Label("Maximum value allowed"), 2, 3, 0, 1)
		self.table.attach(gtk.Label("Minimum value allowed"), 3, 4, 0, 1)
		self.table.attach(gtk.Label("Is nillable? "), 4, 5, 0, 1)
		self.table.attach(gtk.Label("Is optional? "), 5, 6, 0, 1)
		
		
		pos = 1
		for s in schemas:
			if s.children():
				for elem in s.children():
					child = elem[0]		
					label = gtk.Label()
					label.set_markup("<b><i>%s</i></b> --> %s" % (s.name, child.name))
					self.table.attach(label, 0, 1, pos, pos + 1)
					label = gtk.Label()
					label.set_markup('<span foreground="#4071DC" size="large"><b>%s</b></span>' % child.root.name)
					self.table.attach(label, 1, 2, pos, pos + 1)
					self.table.attach(gtk.Label(str(child.max)), 2, 3, pos, pos + 1)
					self.table.attach(gtk.Label(str(child.min)), 3, 4, pos, pos + 1)
					img = gtk.Image()
					if child.nillable:
						img.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
					else:
						img.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
					img.show()
					self.table.attach(img, 4, 5, pos, pos + 1)
					img = gtk.Image()
					if child.optional():
						img.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
					else:
						img.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
					img.show()
					self.table.attach(img, 5, 6, pos, pos + 1)
					pos += 1
			else:
				self.table.attach(gtk.Label(str(names[pos-1])), 0, 1, pos, pos + 1)
				label = gtk.Label()
				label.set_markup('<span foreground="#4071DC" size="large"><b>%s</b></span>' % s.root.name)
				self.table.attach(label, 1, 2, pos, pos + 1)
				self.table.attach(gtk.Label(str(s.max)), 2, 3, pos, pos + 1)
				self.table.attach(gtk.Label(str(s.min)), 3, 4, pos, pos + 1)
				img = gtk.Image()
				if s.nillable:
					img.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
				else:
					img.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
				img.show()
				self.table.attach(img, 4, 5, pos, pos + 1)
				img = gtk.Image()
				if s.optional():
					img.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
				else:
					img.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
				img.show()
				self.table.attach(img, 5, 6, pos, pos + 1)
				pos += 1
	
	def getWidget(self):
		return self.table
