'''
Created on Aug 10, 2012

@author: "Santiago Diaz M."
'''
from core.data import AUTH_BASIC
from core.data import AUTH_WINDOWS
from core.data import AUTH_UNKNOWN
from core.data import AUTH_WSSE
from core.data import AUTH_NONE
from core.data import STRESS_ITEM_FORMAT
from core.data import BOLD_FORMAT
from controller import exceptions
from ui.IWidget import IWidget
from bs4 import BeautifulSoup
import gtk

class cfgWidget(IWidget):
    
    '''
    This Widget handles the configuration tab
    '''
    
    def __init__(self, wsdlhelper, pm):
        self.project_manager = pm
        self.wsdlhelper = wsdlhelper
        
        IWidget.__init__(self)
        self.conf_dict = {}
        self.server_dict = {}
        self.service_combobox = None
        self.port_combobox = None
        self.auth_combobox = None
        
        self.project_frame = gtk.Frame("Project")
        self.project_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.endpoint_frame = gtk.Frame("EndPoint")
        self.endpoint_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.server_frame = gtk.Frame("Server")
        self.server_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.auth_frame = gtk.Frame("Authentication")
        self.auth_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.service_frame = gtk.Frame("Default service")
        self.service_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.port_frame = gtk.Frame("Default port")
        self.port_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        
        self.save_btn = None
        self.vbox = None
        
    def start(self, conf_list, server_list):
        # Generate labels
        if not conf_list or not server_list:
            raise exceptions.antaresException("Either configuration or settings list parameters are missing for config widget")
        
        # Create widgets (lables, entries, combobox, ...
        for key, value in conf_list.items():
            label = gtk.Label(key.title())
            entry = gtk.Entry(0)
            entry.set_editable(False)
            if not value:
                entry.set_text('')
            else:
                entry.set_text(value)
            self.conf_dict[key] = (label, entry)
            
        for key, value in server_list.items():
            label = gtk.Label(key.title())
            entry = gtk.Entry(0)
            entry.set_editable(False)
            if not value:
                entry.set_text('')
            else:
                entry.set_text(value)
            self.server_dict[key] = (label, entry) 
        
        # Project frame
        label = gtk.Label("View WSDL")
        viewButton = gtk.Button("View WSDL", gtk.STOCK_EXECUTE)
        viewButton.connect("clicked", self.viewWSDL, None)
        self.conf_dict["viewwsdl"] = (label, viewButton)
        
        table = gtk.Table(len(self.conf_dict)-2, 2, True)
        column = 0
        row = 0
        for text in sorted(self.conf_dict.iterkeys()):
            table.attach(self.conf_dict[text][0], column, column+1, row, row+1)
            column += 1
            table.attach(self.conf_dict[text][1], column, column+1, row, row+1)
            column = 0
            row += 1
            
        self.project_frame.add(table)
        
        #EndPoint frame
        items = {}
        items['Service name'] = self.wsdlhelper.wsdl_desc.getServiceName()
        items['Target namespace'] = self.wsdlhelper.wsdl_desc.getNamespace()
        #items['Number of ports'] = str(len(self.wsdlhelper.ws_desc.getPorts()))
        table = gtk.Table(2+len(self.wsdlhelper.wsdl_desc.getPorts()), 2, True)
        row = 0
        for k,v in items.items():
            entry = gtk.Entry(0)
            entry.set_text(v)
            table.attach(gtk.Label(k), 0, 1, row, row+1)
            table.attach(entry, 1, 2, row, row+1)
            row += 1
        
        for port in self.wsdlhelper.wsdl_desc.getPorts():
            table.attach(gtk.Label(port), 0, 1, row, row+1)
            label = gtk.Label()
            label.set_markup(BOLD_FORMAT % (str(len(self.wsdlhelper.wsdl_desc.getOperations(port=port))) + " operations"))
            table.attach(label, 1, 2, row, row+1)
            row += 1
        self.endpoint_frame.add(table)
        
        # Server frame
        table = gtk.Table(len(self.server_dict), 2, True)
        column = 0
        row = 0
        for text in sorted(self.server_dict.iterkeys()):
            table.attach(self.server_dict[text][0], column, column+1, row, row+1)
            column += 1
            table.attach(self.server_dict[text][1], column, column+1, row, row+1)
            column = 0
            row += 1
            
        self.server_frame.add(table)
        
        # Authentication frame
        table = gtk.Table(4, 2, True)
        table.attach(gtk.Label('Type'), 0, 1, 0, 1)
        self.auth_combobox = gtk.combo_box_entry_new_text()
        labels = {AUTH_NONE: 'None', 
                  AUTH_BASIC: 'Basic authentication', AUTH_WINDOWS: 'Negotiate/Windows authentication', 
                  AUTH_WSSE: 'WSSE', AUTH_UNKNOWN: 'Unknown protocol authentication'}
        for label in labels.values():
            self.auth_combobox.append_text(label)

        if not self.project_manager.getAuthType():
            self.auth_combobox.set_active(0)
        else:
            self.auth_combobox.set_active(self.project_manager.getAuthType())
        #Call the appropriate PM function with the correct constant for this type of authentication
        self.auth_combobox.child.connect('changed', self.project_manager.setAuthType, self.auth_combobox.get_active())

        table.attach(self.auth_combobox, 1, 2, 0, 1)
        table.attach(gtk.Label('Domain'), 0, 1, 1, 2)
        entry = gtk.Entry(0)
        entry.set_text(str(self.project_manager.getDomain()))
        entry.connect('focus-out-event', self.project_manager.setDomain, entry.get_text())
        table.attach(entry, 1, 2, 1, 2)
        table.attach(gtk.Label('Username'), 0, 1, 2, 3)
        entry = gtk.Entry(0)
        entry.set_text(str(self.project_manager.getUsername()))
        entry.connect('focus-out-event', self.project_manager.setUsername, entry.get_text())
        table.attach(entry, 1, 2, 2, 3)
        table.attach(gtk.Label('Password'), 0, 1, 3, 4)
        entry = gtk.Entry(0)
        entry.set_text(str(self.project_manager.getPassword()))
        entry.connect('focus-out-event', self.changeAuth, self.project_manager.setPassword, entry.get_text())
        table.attach(entry, 1, 2, 3, 4)
        
        self.auth_frame.add(table)
        
        # Default webService service and port combobox
        self.service_combobox = gtk.combo_box_entry_new_text()
        self.service_combobox.append_text('')
        for service in self.wsdlhelper.getServices():
            self.service_combobox.append_text(service)
            self.service_combobox.child.connect('changed', self.changeService)
        self.service_combobox.set_active(0)
        self.service_frame.add(self.service_combobox)
        
        self.port_combobox = gtk.combo_box_entry_new_text()
        self.port_combobox.append_text('')
        for bind in self.wsdlhelper.getBindings():
            self.port_combobox.append_text(bind.name)
            self.port_combobox.child.connect('changed', self.changeBind)
        self.port_combobox.set_active(0)
        self.port_frame.add(self.port_combobox)
        
        self.vbox = gtk.VBox(False, 0)
        self.vbox.pack_start(self.project_frame, True, True, 0)
        self.vbox.pack_start(self.endpoint_frame, True, True, 0)
        self.vbox.pack_start(self.server_frame, True, True, 0)
        self.vbox.pack_start(self.auth_frame, True, True, 0)
        self.vbox.pack_start(self.service_frame, True, True, 0)
        self.vbox.pack_start(self.port_frame, True, True, 0)
        self.vbox.show_all()
        
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw.add_with_viewport(self.vbox)
        self.sw.show_all()
        
    def getWidget(self):
        return self.sw
    
    def viewWSDL(self, widget, action):
        popup = gtk.Window()
        popup.set_title( "WSDL" )
        popup.set_modal( True )
        popup.resize(600,800)
        popup.set_type_hint( gtk.gdk.WINDOW_TYPE_HINT_DIALOG )
        popup.connect( "destroy", lambda *w:popup.destroy() )
        vb = gtk.VBox(False, 2)
        frame = gtk.Frame('WSDL Contents')
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        buff = gtk.TextBuffer()
        soup = BeautifulSoup(self.project_manager.getWSDLContents())
        buff.set_text(soup.prettify())
        textview = gtk.TextView(buffer=buff)
        textview.set_editable(False)
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
        
    def changeBind(self, entry):
        self.wsdlhelper.setPort(entry.get_text())
    def changeService(self, entry):
        self.wsdlhelper.setService(entry.get_text())
    def changeAuth(self, w, event, entry, id):
            if 1 is id:
                self.project_manager.setDomain(entry.get_text())
            elif 2 is id:
                self.project_manager.setUsername(entry.get_text())
            elif 3 is id:
                self.project_manager.setPassword(entry.get_text())
            elif 4 is id:
                self.project_manager.setAuthType(entry)
    