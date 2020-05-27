"""Implement the graphical user interface for the Logic Simulator.
Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.
Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
import wx.lib.scrolledpanel
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.
    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.
    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.
    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.
    render(self, text): Handles all drawing operations.
    on_paint(self, event): Handles the paint event.
    on_size(self, event): Handles the canvas resize event.
    on_mouse(self, event): Handles mouse events.
    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        
        self.devices = devices
        self.monitors = monitors
        self.names = names
        
        
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, size.height, 0, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        #GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Get canvas size
        size = self.GetClientSize()

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, size.height - 10)
        
        self.device_list = []
        
        self.device_id_list = self.devices.find_devices()
        for device_id in self.device_id_list:
            if self.devices.get_device(device_id).device_kind == self.devices.D_TYPE:
                self.device_list.append("{}.Q".format(self.names.get_name_string(device_id)))
                self.device_list.append("{}.QBAR".format(self.names.get_name_string(device_id)))
            else:
                self.device_list.append(self.names.get_name_string(device_id))
                
        if len(self.device_list) == 0:
            longest_name_len = 0
        else:
            longest_name_len = len(max(self.device_list, key=len))
        
        # Draw signal traces
        j = 0
        for device_id, output_id in self.monitors.monitors_dictionary:
            j += 1
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            self.render_text(monitor_name, 10, (50 * j) - 7, 24)

            # seperator line between traces 
            GL.glColor3f(0.870, 0.411, 0.129)
            GL.glLineWidth(1) 
            GL.glBegin(GL.GL_LINES)
            for i in range(len(signal_list)):
                GL.glVertex2f(0, (50 * j) + 10)
                GL.glVertex2f(size.width, (50 * j) + 10)
            GL.glEnd()

            GL.glBegin(GL.GL_LINES)
            for i in range(len(signal_list)):
                GL.glVertex2f(0, (50 * j) - 40)
                GL.glVertex2f(size.width, (50 * j) - 40)
            GL.glEnd()


            # signal trace
            GL.glColor3f(0.086, 0.356, 0.458)
            GL.glLineWidth(3)
            GL.glBegin(GL.GL_QUADS)
            for i in range(len(signal_list)):
                x = (i * 20) + (longest_name_len * 20)
                x_next = (i * 20) + (longest_name_len * 20) + 20
                base_y = 50*j
                if signal_list[i] == self.devices.HIGH:
                    y = (50 * j) - 25
                elif signal_list[i] == self.devices.LOW:
                    y = (50 * j) - 5
                elif signal_list[i] == self.devices.RISING:
                    y = (50 * j) - 25
                elif signal_list[i] == self.devices.FALLING:
                    y = (50 * j) - 5
                elif signal_list[i] == self.devices.BLANK:
                    y = (50 * j) - 25
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
                GL.glVertex2f(x_next, base_y)
                GL.glVertex2f(x, base_y)
                
            GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y += event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        # if event.GetWheelRotation() < 0:
        #     self.zoom *= (1.0 + (
        #         event.GetWheelRotation() / (20 * event.GetWheelDelta())))
        #     self.init = False
        #     text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
        #                     str(self.zoom)])
        # if event.GetWheelRotation() > 0:
        #     self.zoom /= (1.0 - (
        #         event.GetWheelRotation() / (20 * event.GetWheelDelta())))
        #     self.init = False
        #     text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
        #                     str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, font=12):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        if font == 24:
            font = GLUT.GLUT_BITMAP_HELVETICA_18
        else:
            font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class PopUpFrame(wx.Frame):
    """Class used for pop up window with an error messages"""
    
    def __init__(self, parent, title, text):
        wx.Frame.__init__(self, parent=parent, title=title)
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        label_1 = wx.StaticText(self, wx.ID_ANY, text, style=wx.ALIGN_CENTER)
        self.close_button = wx.Button(self, wx.ID_ANY, "Close")
        
        self.SetBackgroundColour(wx.Colour(0,0,0))
        label_1.SetForegroundColour(wx.Colour(255, 255, 255))
        
        # self.Bind(wx.EVT_MENU, self.on_menu)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button)
        
        sizer_1.Add((20, 20), 1, 0, 0)
        sizer_1.Add(label_1, 1, wx.ALIGN_CENTER, 0)
        sizer_1.Add(self.close_button, 1, wx.ALIGN_CENTER, 0)
        
        self.SetSizer(sizer_1)

        self.Show()
        
    def on_close_button(self, event):
        self.Show(False)
        self.Destroy()


class Gui(wx.Frame):
    """Configure the main window and all the widgets.
    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.
    Parameters
    ----------
    title: title of the window.
    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.
    on_spin(self, event): Event handler for when the user changes the spin
                           control value.
    on_run_button(self, event): Event handler for when the user clicks the run
                                button.
    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors, start_up = False):
        
        self.start_up = start_up

        """Initialise variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.cursor = 0  # cursor position
        self.spin_ctrl_1_value = 10
        self.current_cycles = 10
        self.switch_list = []
        self.device_list = []
        self.monitor_names = []
        self.pathname = None
        self.load_new = False

        self.device_id_list = self.devices.find_devices()
        for device_id in self.device_id_list:
            if self.devices.get_device(device_id).device_kind == self.devices.D_TYPE:
                self.device_list.append("{}.Q".format(self.names.get_name_string(device_id)))
                self.device_list.append("{}.QBAR".format(self.names.get_name_string(device_id)))
            else:
                self.device_list.append(self.names.get_name_string(device_id))

        self.switch_id_list = self.devices.find_devices(self.devices.SWITCH)
        for switch in self.switch_id_list:
            self.switch_list.append(self.names.get_name_string(switch))
        
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            self.monitor_names.append(monitor_name)
    
        if len(self.switch_list) == 0:
            self.choice_1_selection = ""
            self.switch_list = [""]
        else:
            self.choice_1_selection = self.switch_list[0]
        self.choice_2_selection = 0
        if len(self.device_list) == 0:
            self.choice_3_selection = ""
            self.device_list = [""]
        else:
            self.choice_3_selection = self.device_list[0]

        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1000, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors, names)

        # Panel for monitoring signals
        self.panel = wx.lib.scrolledpanel.ScrolledPanel(self)
        self.panel.SetupScrolling()
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Configure left panel widgets
        monitors_label = wx.StaticText(self.panel, wx.ID_ANY, "Signals to Monitor")
        monitors_label.SetForegroundColour(wx.Colour(255, 255, 255))
        panel_sizer.Add(monitors_label, 1, wx.ALIGN_CENTER | wx.TOP, 20)

        # Configure checkboxes for all devices in the circuit
        j=30
        cb_dict = {}
        for i in range(len(self.device_list)):
            j += 40 
            cb = wx.CheckBox(self.panel, label=self.device_list[i], pos=(20, j), size=(100,40))
            cb.SetBackgroundColour(wx.Colour(243, 201, 62))
            panel_sizer.Add(cb, 0, wx.EXPAND | wx.ALL, 20)

            if self.device_list[i] in self.monitor_names:
                cb.SetValue(True)

            # Bind checkbox event to left panel widgets 
            cb.Bind(wx.EVT_CHECKBOX, self.on_checkbox)
            cb_dict.update({cb:device_list[i])

        self.panel.SetSizer(panel_sizer)

        # Configure right panel widgets
        label_1 = wx.StaticText(self, wx.ID_ANY, "Cycles")
        label_2 = wx.StaticText(self, wx.ID_ANY, "Switch")
        label_3 = wx.StaticText(self, wx.ID_ANY, "CONTROLS")
        label_4 = wx.StaticText(self, wx.ID_ANY, "Monitor")
        self.spin_ctrl_1 = wx.SpinCtrl(self, wx.ID_ANY, "10", min=0, max=100)
        self.choice_1 = wx.Choice(self, wx.ID_ANY, choices=self.switch_list)
        self.choice_2 = wx.Choice(self, wx.ID_ANY, choices=["0", "1"])
        self.choice_3 = wx.Choice(self, wx.ID_ANY, choices=self.device_list)
        self.button_1 = wx.Button(self, wx.ID_ANY, "Continue")
        self.button_2 = wx.Button(self, wx.ID_ANY, "Run")
        self.button_3 = wx.Button(self, wx.ID_ANY, "Set")
        self.button_4 = wx.Button(self, wx.ID_ANY, "Set")
        self.button_5 = wx.Button(self, wx.ID_ANY, "Zap")
        self.load_button = wx.Button(self, wx.ID_ANY, "Load")
    
        # Configure the widget properties
        self.SetBackgroundColour(wx.Colour(0,0,0))
        label_1.SetForegroundColour(wx.Colour(255, 255, 255))
        label_2.SetForegroundColour(wx.Colour(255, 255, 255))
        label_3.SetForegroundColour(wx.Colour(255, 255, 255))
        label_3.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        label_4.SetForegroundColour(wx.Colour(255, 255, 255))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin_ctrl_1.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl_1)
        self.choice_1.Bind(wx.EVT_CHOICE, self.on_choice_1)
        self.choice_2.Bind(wx.EVT_CHOICE, self.on_choice_2)
        self.choice_3.Bind(wx.EVT_CHOICE, self.on_choice_3)
        self.button_1.Bind(wx.EVT_BUTTON, self.on_button_1)
        self.button_2.Bind(wx.EVT_BUTTON, self.on_button_2)
        self.button_3.Bind(wx.EVT_BUTTON, self.on_button_3)
        self.button_4.Bind(wx.EVT_BUTTON, self.on_button_4)
        self.button_5.Bind(wx.EVT_BUTTON, self.on_button_5)
        self.load_button.Bind(wx.EVT_BUTTON, self.on_load_button)
    

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)


        main_sizer.Add(self.panel, 2, wx.EXPAND | wx.ALIGN_LEFT, 0)
        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)
    
        side_sizer.Add(sizer_1, 1, wx.ALL, 0)
        side_sizer.Add(sizer_2, 1, wx.ALL, 5)
        side_sizer.Add(sizer_3, 1, wx.ALL, 0)
        side_sizer.Add(sizer_4, 1, wx.ALL, 10)
        side_sizer.Add(sizer_5, 1, wx.ALL, 0)
        side_sizer.Add(sizer_6, 1, wx.ALL, 10)
        side_sizer.Add(sizer_7, 1, wx.ALL, 0)
        side_sizer.Add(sizer_8, 1, wx.ALL, 10)
    
        sizer_1.Add(label_3, 1, wx.ALL, 10)
    
        sizer_2.Add(label_1, 1, wx.ALL, 10)
        sizer_2.Add(self.spin_ctrl_1, 0, wx.ALL, 10)
    
        sizer_3.Add(self.button_1, 1, wx.ALL, 10)
        sizer_3.Add(self.button_2, 1, wx.ALL, 10)
    
        sizer_4.Add(label_2, 1, wx.ALL, 10)
        sizer_4.Add(self.choice_1, 1, wx.ALL, 10)
    
        sizer_5.Add(self.choice_2, 1, wx.ALL, 10)
        sizer_5.Add(self.button_3, 1, wx.ALL, 10)
    
        sizer_6.Add(label_4, 1, wx.ALL, 10)
        sizer_6.Add(self.choice_3, 1, wx.ALL, 10)
    
        sizer_7.Add(self.button_4, 1, wx.ALL, 10)
        sizer_7.Add(self.button_5, 1, wx.ALL, 10)
    
        sizer_8.Add(self.load_button, 1, wx.ALL, 0)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_checkbox(self, event):
        """Handle the event when the user checks a checkbox."""
        sender = event.GetEventObject()
        isChecked = sender.GetValue()

        if isChecked:
            self.

    def on_spin_ctrl_1(self, event):
        """Handle the event when the user changes the cycles spin control value."""
        self.spin_ctrl_1_value = self.spin_ctrl_1.GetValue()
        text = "".join(["New spin control 1 value: ", str(self.spin_ctrl_1_value)])
        self.canvas.render(text)
        
    def on_choice_1(self, event):
        """Handle the event when the user changes the switch selection."""
        self.choice_1_index = self.choice_1.GetCurrentSelection()
        self.choice_1_selection = self.choice_1.GetString(self.choice_1_index)
        text = "".join(["New choice 1 selection: ", str(self.choice_1_selection)])
        self.canvas.render(text)
    
    def on_choice_2(self, event):
        """Handle the event when the user changes the switch state selection."""
        self.choice_2_index = self.choice_2.GetCurrentSelection()
        self.choice_2_selection = self.choice_2.GetString(self.choice_2_index)
        text = "".join(["New choice 2 selection: ", str(self.choice_2_selection)])
        self.canvas.render(text)
        
    def on_choice_3(self, event):
        """Handle the event when the user changes the monitor selection."""
        self.choice_3_index = self.choice_3.GetCurrentSelection()
        self.choice_3_selection = self.choice_3.GetString(self.choice_3_index)
        text = "".join(["New choice 3 selection: ", str(self.choice_3_selection)])
        self.canvas.render(text)

    def on_button_1(self, event):
        """Handle the event when the user clicks button 1 (Continue)."""
        if self.start_up == True:
            text = "No definition file loaded."
            frame = PopUpFrame(self, title="Error!", text=text)
        else:
            text = "Continue button pressed."
            self.current_cycles = self.spin_ctrl_1_value
            self.continue_command()
            self.canvas.render(text)

    def on_button_2(self, event):
        """Handle the event when the user clicks button 2 (Run)."""
        if self.start_up == True:
            text = "No definition file loaded."
            frame = PopUpFrame(self, title="Error!", text=text)
        else:
            text = "Run button pressed."
            self.current_cycles = self.spin_ctrl_1_value
            self.run_command()
            self.canvas.render(text)
        
    def on_button_3(self, event):
        """Handle the event when the user clicks button 3 (Set)."""
        if self.start_up == True:
            text = "No definition file loaded."
            frame = PopUpFrame(self, title="Error!", text=text)
        else:
            text = "Set button pressed."
            self.switch_command()
            self.canvas.render(text)
        
    def on_button_4(self, event):
        """Handle the event when the user clicks button 4 (Set)."""
        if self.start_up == True:
            text = "No definition file loaded."
            frame = PopUpFrame(self, title="Error!", text=text)
        else:    
            text = "Set button pressed."
            self.monitor_command()
            self.canvas.render(text)
        
    def on_button_5(self, event):
        """Handle the event when the user clicks button 5 (Zap)."""
        if self.start_up == True:
            text = "No definition file loaded."
            frame = PopUpFrame(self, title="Error!", text=text)
        else:
            text = "Zap button pressed."
            self.zap_command()
            self.canvas.render(text)
        
    def on_load_button(self, event):
        """Handle the event when the user clicks load button."""

        with wx.FileDialog(self, "Open Definition file", wildcard="Definition files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 

            self.pathname = fileDialog.GetPath()
            # try:
            #     with open(pathname, 'r') as file:
            #         print('Here')
            # except IOError:
            #     wx.LogError("Cannot open file '%s'." % newfile)
        self.load_new = True
        self.Show(False)
        self.Destroy()
        

    def read_name(self, name_string):
        """Return the name ID of the current string if valid.
        Return None if the current string is not a valid name string.
        """
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            pass
        return name_id

    def read_signal_name(self, signal_name):
        """Return the device and port IDs of the current signal name.
        Return None if either is invalid.
        """
        if signal_name.isalnum():
            device_id = self.read_name(signal_name)
            port_id = None
        elif ".QBAR" in signal_name:
            device_id = self.read_name(signal_name[:-5])
            port_id = self.read_name("QBAR")
        else:
            device_id = self.read_name(signal_name[:-2])
            port_id = self.read_name("Q")
        return [device_id, port_id]

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name(self.choice_1_selection)
        if switch_id is not None:
            switch_state = self.choice_2_selection
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    text = "Switch {} set to {}.".format(self.choice_1_selection, switch_state)
                    frame = PopUpFrame(self, title="Success!", text=text)
                    

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name(self.choice_3_selection)
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                pass
            else:
                text = "Already monitoring {}.".format(self.choice_3_selection)
                frame = PopUpFrame(self, title="Error!", text=text)
                

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name(self.choice_3_selection)
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                pass
            else:
                text = "Not currently monitoring {}.".format(self.choice_3_selection)
                frame = PopUpFrame(self, title="Error!", text=text)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.
        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                text = "Network oscillating."
                frame = PopUpFrame(self, title="Error!", text=text)
                return False
        return True
   
    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.spin_ctrl_1_value

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        # cycles = self.read_number(0, None)
        cycles = self.spin_ctrl_1_value
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                text = "Nothing to continue. Run first."
                frame = PopUpFrame(self, title="Error!", text=text)
            elif self.run_network(cycles):
                self.cycles_completed += cycles
