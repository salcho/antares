'''
Created on Feb 12, 2013

@author: Santiago Diaz
'''

import gtk
from bs4 import BeautifulSoup
from ui.IWidget import IWidget
from suds import WebFault
from core.WSDLHelper import WSDLHelper

class TestRequestWidget(IWidget):
	'''
	TestRequestWidget used to send test requests to be later compared with injection requests
	IMPORTANT: This widget needs to be started!
	'''

	def __init__(self, wsdlh, pm):
		self.pm = pm
		self.wsdlhelper = wsdlh
		IWidget.__init__(self)
		self.oCombobox = None
		self.opName = None
		
		self.results_vbox = gtk.VBox(False, 0)
		self.TVRq = None
		self.TVRp = None
		self.inProcess = None

	def start(self):
		frame = gtk.Frame('Methods')
		frame2 = gtk.Frame('Request/Response')
		frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		frame2.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.oCombobox = gtk.combo_box_entry_new_text()
		self.oCombobox.append_text('')

		ops = self.wsdlhelper.getMethods()
		for op in ops:
			self.oCombobox.append_text(op)
			self.oCombobox.child.connect('changed', self.changeOp)
		frame.add(self.oCombobox)
			
		self.results_vbox = gtk.VBox(False, 0)
		hpaned = gtk.HPaned()
		hpaned.show()
		#Create textview for responses
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.TVRq = gtk.TextView(buffer=None)
		self.TVRq.set_editable(True)
		self.TVRq.set_wrap_mode(gtk.WRAP_NONE)
		self.TVRq.set_justification(gtk.JUSTIFY_LEFT)
		self.TVRq.set_cursor_visible(True)
		sw.add_with_viewport(self.TVRq)
		sw.set_size_request(400, -1)
		sw.show_all()
		
		hpaned.pack1(sw, resize=True, shrink=False)
		
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.TVRp = gtk.TextView(buffer=None)
		self.TVRp.set_editable(True)
		self.TVRp.set_wrap_mode(gtk.WRAP_NONE)
		self.TVRp.set_justification(gtk.JUSTIFY_LEFT)
		self.TVRp.set_cursor_visible(True)
		sw.show_all()
		sw.add_with_viewport(self.TVRp)
		sw.set_size_request(400, -1)
		
		frame3 = gtk.Frame('Actions')
		box = gtk.HButtonBox()
		box.set_spacing(gtk.BUTTONBOX_SPREAD)
		btnSend = gtk.Button('Send', gtk.STOCK_EXECUTE)
		btnSend.connect('clicked', self.sendRx, None)
		btnCdata = gtk.Button('Add CDATA block')
		btnCdata.connect('clicked', self.addCDATA)
		btnCmnt = gtk.Button('Comment selection')
		btnCmnt.connect('clicked', self.comment)
		btn_http = gtk.Button('Get HTTP message')
		btn_http.connect('clicked', self.copyHTTPMessage)
		btn_addr = gtk.Button('Add WS-Addressing')
		btn_addr.connect('clicked', self.addAddressing)
		self.inProcess = gtk.Image()
		self.inProcess.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
		box.add(btnSend)
		box.add(btnCdata)
		box.add(btnCmnt)
		box.add(btn_http)
		box.add(btn_addr)
		box.add(self.inProcess)
		frame3.add(box)
		
		hpaned.pack2(sw, resize=True, shrink=False)
		frame2.add(hpaned)
		self.results_vbox.pack_start(frame, False, False, 0)
		self.results_vbox.pack_start(frame2, True, True, 0)
		self.results_vbox.pack_start(frame3, False, False, 0)
		self.results_vbox.show_all()


	def sendRx(self, widget, data):
		self.inProcess.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
		self.inProcess.show()
		buf = self.TVRq.get_buffer()
		start, end = buf.get_bounds()
		
		try:
			xml = self.wsdlhelper.sendRaw(self.opName, buf.get_text(start, end))
			while gtk.events_pending():
				gtk.main_iteration(False)

			buf = self.TVRp.get_buffer()
			buf.set_text(str(xml))
			
			self.inProcess.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
			self.inProcess.show()
		except Exception as e:
			buf = self.TVRp.get_buffer()
			buf.set_text(str(e))

	def changeOp(self, entry):
		if entry.get_text() != '':
			if self.opName != entry.get_text():
				self.opName = entry.get_text()
				self.inProcess.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
				#while gtk.events_pending():
				#	gtk.main_iteration(False)
				self.inProcess.show()

				req, res = self.wsdlhelper.getRqRx(self.opName)
				buf = self.TVRq.get_buffer()
				buf.set_text(str(req)) if req else buf.set_text('ERROR CREATING REQUEST')
				buf = self.TVRp.get_buffer()
				buf.set_text(str(res)) if res else buf.set_text('ERROR CREATING RESPONSE')
				
				if req and res:	
					self.inProcess.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
				else:
					self.inProcess.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
					
				self.inProcess.show()

	def refresh(self, widget):
		ops = self.wsdlhelper.getMethods()
		self.oCombobox = gtk.combo_box_new_text()
		self.oCombobox.append_text('')
		for op in ops:
			self.oCombobox.append_text(op)
			self.oCombobox.connect('changed', self.changeOp)
		self.oCombobox.connect('popdown', self.refresh)
		
	def comment(self, widget):
		buf = self.TVRq.get_buffer()
		if buf.get_selection_bounds() != ():
			start, end = buf.get_selection_bounds()
			markBnd = buf.create_mark('init', start, True)
			buf.insert(end, '-->')
			buf.insert(buf.get_iter_at_mark(markBnd), '<!--')
		self.TVRq.set_buffer(buf)
			

	def addCDATA(self, widget):
		#pos = self.TVRq.get_iter_location()
		#iter = self.TVRq.get_iter_at_location(pos)
		buf = self.TVRq.get_buffer()
		buf.insert_at_cursor('<![CDATA[  ]]>')
		self.TVRq.set_buffer(buf)
		#buf.insert(iter, '<![CDATA[  ]]> ')

	def getWidget(self):
		return self.results_vbox
	
	def copyHTTPMessage(self, widget):
		"""
		Generate a simple HTTP Message to call this service from other tools
		"""
		if not self.opName:
			return
		popup = gtk.Window()
		popup.set_title( "HTTP Message" )
		popup.set_modal( True )
		popup.resize(600,500)
		popup.set_type_hint( gtk.gdk.WINDOW_TYPE_HINT_DIALOG )
		popup.connect( "destroy", lambda *w:popup.destroy() )
		vb = gtk.VBox(False, 2)
		frame = gtk.Frame('*')
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		buff = gtk.TextBuffer()
		# Get object's path from URL
		pkt = "POST /%s HTTP/1.1\n" %  "/".join(self.pm.getURL().split('/')[3:])
		# Get IP
		pkt += "Host: %s\n" % self.pm.getURL().split('/')[2]
		pkt += "Content-Type: text/xml; charset=utf-8\n"
		# Get SOAPAction header
		pkt += "SOAPAction: %s\n" % self.wsdlhelper.getSOAPActionHeader(self.opName)
		# Get XML
		content = self.TVRq.get_buffer().get_text(*self.TVRq.get_buffer().get_bounds()) + "\n\n"
		pkt += "Content-Length: %d\n\n" % len(content)
		pkt += content
		#soup = BeautifulSoup(pkt)
		buff.set_text(pkt)
		textview = gtk.TextView(buffer=buff)
		textview.set_editable(True)
		textview.set_wrap_mode(gtk.WRAP_NONE)
		textview.set_justification(gtk.JUSTIFY_LEFT)
		textview.set_cursor_visible(True)
		sw.show_all()
		sw.add_with_viewport(textview)
		sw.set_size_request(400, -1)
		vb.pack_start(sw, True, True, 0)
		btn = gtk.Button('Close', gtk.STOCK_CLOSE)
		btn.connect('clicked', lambda *w: popup.destroy() )
		vb.pack_start(btn, False, False, 0)
		frame.add(vb)
		popup.add(frame)
		popup.show_all()

	def addAddressing(self, widget):
		"""
		Get the user a request template using WS-Addressing
		"""
		if not self.opName:
			return

