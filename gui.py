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
import ntpath
import math
import time
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

    def __init__(self, parent, devices, monitors, names, start_up):
        """Initialise canvas properties and useful variables."""
        self.devices = devices
        self.monitors = monitors
        self.names = names
        self.start_up = start_up
        self.last_vertical = 0
        self.last_horizontal = 0

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
        self.Bind(wx.EVT_KEY_DOWN, self.on_keydown)

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

        self.device_list = []

        if self.start_up is False:
            self.device_id_list = self.devices.find_devices()
            for device_id in self.device_id_list:
                if self.devices.get_device(device_id).device_kind == \
                        self.devices.D_TYPE:
                    self.device_list.append("{}.Q".format(
                        self.names.get_name_string(device_id)))
                    self.device_list.append("{}.QBAR".format(
                        self.names.get_name_string(device_id)))
                else:
                    self.device_list.append(self.names.get_name_string(
                        device_id))

            if len(self.device_list) == 0:
                longest_name_len = 0
            else:
                longest_name_len = len(max(self.device_list, key=len))
            self.offset = longest_name_len

            # Draw signal traces
            j = 1
            for device_id, output_id in self.monitors.monitors_dictionary:
                j += 1
                monitor_name = self.devices.get_signal_name(
                    device_id, output_id)
                signal_list = self.monitors.monitors_dictionary[
                    (device_id, output_id)]
                self.render_text(monitor_name, 10, (50 * j) - 18, 24)
                self.cycles = len(signal_list)

                # seperator line between traces
                GL.glColor3f(0.870, 0.411, 0.129)
                GL.glLineWidth(1)
                GL.glBegin(GL.GL_LINES)
                # for i in range(len(signal_list)):
                GL.glVertex2f(0, (50 * j))
                GL.glVertex2f(self.cycles * 20 + 1000, (50 * j))
                GL.glEnd()

                GL.glBegin(GL.GL_LINES)
                # for i in range(len(signal_list)):
                GL.glVertex2f(0, (50 * j) - 50)
                GL.glVertex2f(self.cycles * 20 + 1000, (50 * j) - 50)
                self.last_horizontal = (50 * j) - 50
                GL.glEnd()

                # vertical lines
                for i in range(len(signal_list) + 1):

                    if i % 5 == 0 and j == 2:
                        if i == 0 or i == 5:
                            x = (i * 20) + (longest_name_len * 20) - 2.5
                        else:
                            x = (i * 20) + (longest_name_len * 20) - 5
                        self.render_text(str(i), x, (50 * j) - 60, 24)

                GL.glBegin(GL.GL_LINES)
                GL.glColor3f(0.870, 0.411, 0.129)

                for i in range(len(signal_list) + 1):

                    if i % 5 == 0:
                        x = (i * 20) + (longest_name_len * 20)
                        GL.glVertex2f(x, (50 * j))
                        GL.glVertex2f(x, (50 * j) - 55)

                GL.glEnd()

                # signal trace
                GL.glColor3f(0.086, 0.356, 0.458)
                GL.glLineWidth(2)
                GL.glBegin(GL.GL_LINES)
                first_run = True
                blank = False
                for i in range(len(signal_list)):
                    GL.glColor3f(0.086, 0.356, 0.458)
                    x = (i * 20) + (longest_name_len * 20)
                    x_next = (i * 20) + (longest_name_len * 20) + 20
                    base_y = (50*j) - 11
                    if signal_list[i] == self.devices.HIGH:
                        y = base_y - 25
                    elif signal_list[i] == self.devices.LOW:
                        y = base_y - 5
                    elif signal_list[i] == self.devices.RISING:
                        y = base_y - 25
                    elif signal_list[i] == self.devices.FALLING:
                        y = base_y - 5
                    elif signal_list[i] == self.devices.BLANK:
                        blank = True
                    if first_run is False:
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y)
                        GL.glColor3f(0.086, 0.356, 0.458)
                        GL.glVertex2f(x_next, y)
                    elif blank is True:
                        blank = False
                        pass
                    else:
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y)
                        GL.glColor3f(0.086, 0.356, 0.458)
                        GL.glVertex2f(x_next, y)
                        first_run = False

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

        self.Refresh()  # triggers the paint event

        self.SetCurrent(self.context)

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

    def on_keydown(self, event):
        """Handle keydown events."""
        text = ""
        keycode = event.GetKeyCode()
        size = self.GetClientSize()

        if keycode == wx.WXK_RIGHT:

            if self.pan_x <= - self.cycles * 20 - \
                    self.offset * 20 - 100 + size.width:
                pass
            else:
                self.pan_x -= 50
            self.init = False
            text = "Right Arrow Key"

        if keycode == wx.WXK_LEFT:

            if self.pan_x >= 0:
                pass
            else:
                self.pan_x += 50
            self.init = False
            text = "Left Arrow Key"

        if keycode == wx.WXK_UP:

            if self.pan_y >= 0:
                pass
            else:
                self.pan_y += 50
            self.init = False
            text = "Up Arrow Key"

        if keycode == wx.WXK_DOWN:

            if self.pan_y <= - self.last_horizontal + size.height - 50:
                pass
            else:
                self.pan_y -= 50
            self.init = False
            text = "Down Arrow Key"

        self.Refresh()  # triggers the paint event

    def move_right(self):
        """Handle automatic right scrolling events."""
        size = self.GetClientSize()

        if self.pan_x <= - (self.cycles+1) * 20 - \
                self.offset * 20 - 100 + size.width:
            pass
        else:
            self.pan_x -= 20
        self.init = False

        self.Refresh()  # triggers the paint event

    def zero_canvas(self):
        """Handle moving canvas back to x=0."""
        self.pan_x = 0
        self.init = False

        self.Refresh()  # triggers the paint event


class PopUpFrame(wx.Frame):
    """Class used for pop up window with an error/success messages."""

    def __init__(self, parent, title, text):
        """Initialise variables."""
        wx.Frame.__init__(self, parent=parent, title=title)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        label_1 = wx.StaticText(self, wx.ID_ANY, text, style=wx.ALIGN_LEFT)
        self.close_button = wx.Button(self, wx.ID_ANY, _("Close"))

        self.SetBackgroundColour(wx.Colour(40, 40, 40))
        label_1.SetForegroundColour(wx.Colour(255, 255, 255))

        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button)

        sizer_1.Add((20, 20), 1, 0, 0)
        sizer_1.Add(label_1, 1, wx.ALIGN_CENTRE, 20)
        sizer_1.Add(self.close_button, 1, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        self.SetSizer(sizer_1)
        # self.SetSizeHints(400, 300, maxW=400, maxH=300)

        self.Show()

    def on_close_button(self, event):
        """Handle the event when the user clicks the close button."""
        self.Show(False)
        self.Destroy()


class DefinitionErrors(wx.Frame):
    """Class used for pop up window with definition file error messages."""

    def __init__(self, parent, title, text, tabs, overview):
        """Initialise variables."""
        wx.Frame.__init__(self, parent=parent, title=title, size=(600, 560))

        self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=wx.NB_RIGHT)

        self.notebook_1_panes = []
        self.text_list = []

        for i in range(len(text)):
            self.notebook_1_panes.append(wx.Panel(self.notebook_1, wx.ID_ANY))
            self.text_list.append(text[i])

        self.close_button = wx.Button(
            self.notebook_1_panes[-1], wx.ID_ANY, _("Close"))
        self.overview = wx.StaticText(
            self.notebook_1_panes[0], wx.ALIGN_LEFT, overview)
        self.overview.SetForegroundColour(wx.Colour(255, 255, 255))
        self.overview.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                              0, ""))

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.sizers = []
        self.labels = []

        for i in range(len(text)):
            self.sizers.append(wx.BoxSizer(wx.VERTICAL))
            self.labels.append(wx.StaticText(self.notebook_1_panes[i],
                               wx.ID_ANY, self.text_list[i]))
            self.labels[i].SetForegroundColour(wx.Colour(255, 255, 255))
            self.labels[i].SetFont(wx.Font(12, wx.FONTFAMILY_MODERN,
                                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                   0, ""))

        self.SetOwnBackgroundColour(wx.Colour(40, 40, 40))
        self.notebook_1.SetBackgroundColour(wx.Colour(40, 40, 40))

        self.sizers[0].Add(self.overview, 1, wx.ALIGN_LEFT, 0)

        for i in range(len(text)):
            self.sizers[i].Add(self.labels[i], 1, wx.EXPAND, 0)

            self.notebook_1_panes[i].SetSizer(self.sizers[i])

            self.notebook_1.AddPage(self.notebook_1_panes[i], tabs[i])

        self.sizers[-1].Add(self.close_button, 1,
                            wx.ALIGN_CENTER | wx.BOTTOM, 20)

        for i in range(len(self.sizers)):
            if i + 1 != len(self.sizers):
                self.sizers[i].Add((20, 20), 1, wx.ALIGN_CENTER, 10)

        sizer_1.Add(self.notebook_1, 1, wx.ALL, 0)

        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button)

        self.SetSizeHints(600, 560)

        self.SetSizer(sizer_1)
        self.Show()

    def on_close_button(self, event):
        """Handle the event when the user clicks the close button."""
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

    def __init__(self, title, path, names, devices, network,
                 monitors, filename, start_up=False):
        """Initialise variables."""
        self.start_up = start_up
        self.pathname = path
        self.filename = filename
        self.current_pathname = self.pathname
        self.current_filename = self.filename
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
        self.switch_high_list = []
        self.device_list = []
        self.monitor_names = []
        self.load_new = False
        self.continuous_speed = 450
        self.slider_position = 450
        self.continuous_running = False

        if self.start_up is False:
            self.device_id_list = self.devices.find_devices()
            for device_id in self.device_id_list:
                if self.devices.get_device(device_id).device_kind == \
                        self.devices.D_TYPE:
                    self.device_list.append("{}.Q".format(
                        self.names.get_name_string(device_id)))
                    self.device_list.append("{}.QBAR".format(
                        self.names.get_name_string(device_id)))
                else:
                    self.device_list.append(
                        self.names.get_name_string(device_id))

            self.switch_id_list = self.devices.find_devices(
                self.devices.SWITCH)
            for switch in self.switch_id_list:
                self.switch_list.append(self.names.get_name_string(switch))

            for switch in self.switch_id_list:
                switch_device = self.devices.get_device(switch)
                if switch_device.outputs[None] == 0:
                    self.switch_high_list.append(
                        self.names.get_name_string(switch))

            for device_id, output_id in self.monitors.monitors_dictionary:
                monitor_name = self.devices.get_signal_name(
                    device_id, output_id)
                self.monitor_names.append(monitor_name)

        if len(self.device_list) == 0:
            self.choice_3_selection = ""
            self.device_list = [""]
        else:
            self.choice_3_selection = self.device_list[0]

        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1500, 650))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        menuBar.Append(fileMenu, _("&File"))
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors, names, self.start_up)

        # LEFT PANEL FOR MONITORING SIGNALS
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        all_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Configure left panel widgets
        monitors_label = wx.StaticText(self,
                                       wx.ID_ANY, _("SIGNALS TO MONITOR"))
        self.all_button = wx.Button(self, wx.ID_ANY, _("ALL"))
        # add lang
        self.deselect_all_button = wx.Button(self, wx.ID_ANY, _("NONE"))
        monitors_label.SetForegroundColour(wx.Colour(243, 201, 62))
        monitors_label.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT,
                               wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                               0, ""))
        panel_sizer.Add(monitors_label, 0, wx.CENTER | wx.TOP, 20)

        # Configure checkboxes for all devices in the circuit
        self.cbList = wx.CheckListBox(self, -1, (20, 40), (200, 400),
                                      choices=self.device_list,
                                      style=wx.ALIGN_RIGHT)
        self.cbList.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                            0, "MS Shell Dlg 2"))
        # Add buttons below checklistbox
        all_button_sizer.Add(self.all_button, 1, wx.ALL, 10)
        all_button_sizer.Add(
            self.deselect_all_button, 1, wx.ALL, 10)

        panel_sizer.Add(self.cbList, 1, wx.EXPAND | wx.ALL, 20)
        panel_sizer.Add(all_button_sizer, 1, wx.CENTER | wx.BOTTOM, 20)

        # Tick boxes for monitors specified in definition file
        for i in range(len(self.device_list)):
            if self.device_list[i] in self.monitor_names:
                self.cbList.Check(i, check=True)

        # bind checklistbox to checkbox event
        self.cbList.Bind(wx.EVT_CHECKLISTBOX, self.on_monitor_checkbox)
        self.all_button.Bind(wx.EVT_BUTTON, self.on_all)
        self.deselect_all_button.Bind(wx.EVT_BUTTON, self.on_de_all)

        # RIGHT PANEL FOR CONTROLS
        # Configure right panel widgets
        label_1 = wx.StaticText(self, wx.ID_ANY, _("Cycles"))
        label_3 = wx.StaticText(self, wx.ID_ANY, _("CONTROLS"))
        label_4 = wx.StaticText(self, wx.ID_ANY,
                                _("Select to set switch to HIGH"))
        label_5 = wx.StaticText(self, wx.ID_ANY, _("Speed"))
        self.spin_ctrl_1 = wx.SpinCtrl(self, wx.ID_ANY, "10", min=0, max=40)
        self.button_1 = wx.Button(self, wx.ID_ANY, _("Continue"))
        self.button_2 = wx.Button(self, wx.ID_ANY, _("Run"))
        self.load_button = wx.Button(self, wx.ID_ANY, _("Load New"))
        self.reset_button = wx.Button(self, wx.ID_ANY, _("Reset"))

        self.continuous_label = wx.StaticText(
            self, wx.ID_ANY, _("Continuous Mode"))
        
        self.startstop_button = wx.Button(self, wx.ID_ANY, _("Start/Stop"))
        self.speed_slider = wx.Slider(self, wx.ID_ANY, 500,
                                      minValue=1, maxValue=900)

        # Checkbox for switches
        self.cbList2 = wx.CheckListBox(self, -1, (20, 40), (200, 200),
                                       choices=self.switch_list,
                                       style=wx.ALIGN_RIGHT)
        self.cbList2.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                             0, "MS Shell Dlg 2"))
        # Tick boxes for switches set to high
        for i in range(len(self.switch_list)):
            if self.switch_list[i] in self.switch_high_list:
                self.cbList2.Check(i, check=True)

        # Configure the widget properties
        self.SetBackgroundColour(wx.Colour(40, 40, 40))
        label_1.SetForegroundColour(wx.Colour(255, 255, 255))
        label_3.SetForegroundColour(wx.Colour(243, 201, 62))
        label_3.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_NORMAL, 0, ""))
        label_4.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_NORMAL, 0, ""))
        label_4.SetForegroundColour(wx.Colour(255, 255, 255))
        label_5.SetForegroundColour(wx.Colour(255, 255, 255))
        self.continuous_label.SetForegroundColour(wx.Colour(255, 255, 255))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin_ctrl_1.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl_1)
        self.button_1.Bind(wx.EVT_BUTTON, self.on_button_1)
        self.button_2.Bind(wx.EVT_BUTTON, self.on_button_2)
        self.load_button.Bind(wx.EVT_BUTTON, self.on_load_button)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset_button)
        self.startstop_button.Bind(wx.EVT_BUTTON, self.on_startstop_button)
        self.speed_slider.Bind(wx.EVT_SCROLL, self.on_speed_slider)
        self.cbList2.Bind(wx.EVT_CHECKLISTBOX, self.on_switch_checkbox)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_0 = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)

        side_sizer.Add(label_3, 0, wx.CENTER | wx.TOP, 20)
        side_sizer.Add(sizer_0, 1, wx.EXPAND | wx.BOTTOM, 0)
        side_sizer.Add((5, 5), 1, 0, 0)
        side_sizer.Add(sizer_5, 1, wx.EXPAND | wx.TOP, 0)
        side_sizer.Add((5, 5), 1, 0, 0)
        side_sizer.Add(sizer_6, 1, wx.EXPAND | wx.TOP, 0)
        side_sizer.Add((5, 5), 1, 0, 0)
        side_sizer.Add(sizer_7, 1, wx.EXPAND | wx.TOP, 0)

        sizer_0.Add(sizer_1, 1, wx.EXPAND | wx.ALL, 5)
        sizer_0.Add(sizer_2, 1, wx.EXPAND | wx.ALL, 5)

        sizer_1.Add(label_1, 1, wx.ALL, 10)
        sizer_1.Add(self.spin_ctrl_1, 0, wx.ALL, 10)

        sizer_2.Add(self.button_1, 1, wx.ALL, 10)
        sizer_2.Add(self.button_2, 1, wx.ALL, 10)

        sizer_4.Add(self.continuous_label, 1, wx.ALL, 10)
        sizer_4.Add(self.startstop_button, 1, wx.ALL, 10)

        sizer_5.Add(sizer_4, 0, wx.CENTRE | wx.BOTTOM, 10, 0)
        sizer_5.Add(label_5, 0, wx.CENTRE | wx.BOTTOM, 1)
        sizer_5.Add(self.speed_slider, 1, wx.CENTRE | wx.ALL, 10)

        sizer_6.Add(label_4, 0, wx.CENTRE, 0)
        sizer_6.Add(self.cbList2, 0, wx.CENTRE, 0)

        sizer_7.Add(self.load_button, 1, wx.ALL, 10)
        sizer_7.Add(self.reset_button, 1, wx.ALL, 10)

        main_sizer.Add(panel_sizer, 2, wx.ALIGN_LEFT | wx.EXPAND, 0)
        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        self.SetSizeHints(600, 650)
        self.SetSizer(main_sizer)

        self.Maximize(True)

    def update(self, event):
        """Handle the event when the timer is running."""
        text = ""
        self.continuous_command()
        self.canvas.move_right()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(_("Logic Simulator\nCreated by Mojisola\
                            Agboola\n2017", "About Logsim"),
                          wx.ICON_INFORMATION | wx.OK)

    def on_monitor_checkbox(self, event):
        """Handle the event when the user checks a checkbox."""
        index = event.GetSelection()
        self.checked_name = self.cbList.GetString(index)
        text = 'Checkbox ticked'
        if self.cbList.IsChecked(index):
            self.monitor_command()
            self.canvas.render(text)

        if not self.cbList.IsChecked(index):
            self.zap_command()
            self.canvas.render(text)

    def on_all(self, event):
        """Handle the event when the user checks all."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        else:
            text = 'All ticked'
            for i in range(len(self.cbList.Items)):
                if not self.cbList.IsChecked(i):
                    self.cbList.Check(i, True)
                    self.checked_name = self.cbList.GetString(i)
                    self.monitor_command()
            self.canvas.render(text)

    def on_de_all(self, event):
        """Handle the event when the user deselects all."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        else:
            text = 'All ticked'
            for i in range(len(self.cbList.Items)):
                if self.cbList.IsChecked(i):
                    self.cbList.Check(i, False)
                    self.checked_name = self.cbList.GetString(i)
                    self.zap_command()
            self.canvas.render(text)

    def on_switch_checkbox(self, event):
        """Set the specified switch to the specified signal level."""
        index = event.GetSelection()
        self.checked_name = self.cbList2.GetString(index)
        switch_id = self.read_name(self.checked_name)
        if switch_id is not None:
            text = 'Checkbox ticked'
            if self.cbList2.IsChecked(index):
                self.devices.set_switch(switch_id, self.devices.HIGH)

            if not self.cbList2.IsChecked(index):
                self.devices.set_switch(switch_id, self.devices.LOW)

    def on_spin_ctrl_1(self, event):
        """Handle the event when the user changes the cycles value."""
        self.spin_ctrl_1_value = self.spin_ctrl_1.GetValue()
        text = "".join(["New spin control 1 value: ", str(
            self.spin_ctrl_1_value)])
        self.canvas.render(text)

    def on_choice_1(self, event):
        """Handle the event when the user changes the switch selection."""
        self.choice_1_index = self.choice_1.GetCurrentSelection()
        self.choice_1_selection = self.choice_1.GetString(self.choice_1_index)
        text = "".join(["New choice 1 selection: ", str(
            self.choice_1_selection)])
        self.canvas.render(text)

    def on_choice_2(self, event):
        """Handle the event when the user changes the switch selection."""
        self.choice_2_index = self.choice_2.GetCurrentSelection()
        self.choice_2_selection = self.choice_2.GetString(self.choice_2_index)
        text = "".join(["New choice 2 selection: ", str(
            self.choice_2_selection)])
        self.canvas.render(text)

    def on_button_1(self, event):
        """Handle the event when the user clicks button 1 (Continue)."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        else:
            text = "Continue button pressed."
            self.current_cycles = self.spin_ctrl_1_value
            self.continue_command()
            self.canvas.render(text)

    def on_button_2(self, event):
        """Handle the event when the user clicks button 2 (Run)."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        else:
            text = "Run button pressed."
            self.current_cycles = self.spin_ctrl_1_value
            self.run_command()
            self.canvas.zero_canvas()

    def on_button_3(self, event):
        """Handle the event when the user clicks button 3 (Set)."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        else:
            text = "Set button pressed."
            self.switch_command()
            self.canvas.render(text)

    def on_load_button(self, event):
        """Handle the event when the user clicks load button."""
        with wx.FileDialog(
            self, _("Open Definition file"),
            wildcard="Definition files (*.txt)|*.txt",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.pathname = fileDialog.GetPath()

            self.filename = self.path_leaf(self.pathname)

            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(self.pathname, names)
            parser = Parser(names, devices, network, monitors, scanner)
            parser.parse_network()
            error_list = scanner.error_list
            num_errors = len(error_list)

            pages = math.ceil(num_errors/4)

            if num_errors != 0:

                text_list = []
                tab_labels = []

                for i in range(pages-1):
                    tab_labels.append("{}-{}".format(1 + i * 4, 4 + i * 4))
                    label = 4 + i * 4

                if num_errors == 1:
                    tab_labels.append("1")
                elif num_errors <= 4:
                    tab_labels.append("1-{}".format(num_errors))
                else:
                    if (label+1) == num_errors:
                        tab_labels.append("{}".format(num_errors))
                    else:
                        tab_labels.append("{}-{}".format(label+1, num_errors))

                if num_errors == 1:
                    overview = _("\nDefinition file '{}' contains {} error.")\
                        .format(self.filename, num_errors)
                else:
                    overview = _("\nDefinition file '{}' contains {} errors.")\
                        .format(self.filename, num_errors)

                for i in range(pages):
                    if i == 0:
                        text = '\n' + '*'*76 + '\n'
                    else:
                        text = "".format(self.filename, num_errors)
                    for j in range(4):
                        try:
                            text += (error_list[j + i * 4] + "\n")
                        except IndexError:
                            text += ('\n'*8)
                    text_list.append(text)

                frame = DefinitionErrors(self, title=_("Error!"),
                                         text=text_list, tabs=tab_labels,
                                         overview=overview)

                return

        self.current_filename = self.filename
        self.current_pathname = self.pathname
        self.load_new = True
        self.Show(False)
        self.Destroy()

    def on_reset_button(self, event):
        """Handle the event when the user clicks reset button."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        else:
            self.load_new = True
            self.Show(False)
            self.Destroy()

    def on_startstop_button(self, event):
        """Handle the event when the user clicks the stop button."""
        if self.start_up is True:
            text = _("No definition file loaded.")
            frame = PopUpFrame(self, title=_("Error!"), text=text)
        elif self.continuous_running is False:
            self.timer.Start(self.continuous_speed)
            self.continuous_running = True
        else:
            self.timer.Stop()
            self.continuous_running = False

    def on_speed_slider(self, event):
        """Handle the event when the user changes the speed slider."""
        self.slider_position = self.speed_slider.GetValue()
        self.continuous_speed = -self.slider_position + 1001
        if self.continuous_running is True:
            self.timer.Stop()
            self.timer.Start(self.continuous_speed)

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
            if switch_state == "1":
                self.devices.set_switch(switch_id, self.devices.HIGH)
            else:
                self.devices.set_switch(switch_id, self.devices.LOW)
            text = _("Switch {} set to {}.").format(
                   self.choice_1_selection, switch_state)
            frame = PopUpFrame(self, title=_("Success!"), text=text)

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name(self.checked_name)
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                pass
            else:
                text = _("Already monitoring {}.").format(self.checked_name)
                frame = PopUpFrame(self, title=_("Error!"), text=text)

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name(self.checked_name)
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                pass
            else:
                text = _("Not currently monitoring {}.").format(
                    self.checked_name)
                frame = PopUpFrame(self, title=_("Error!"), text=text)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                text = _("Network oscillating.")
                frame = PopUpFrame(self, title=_("Error!"), text=text)
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
                text = _("Nothing to continue. Run first.")
                frame = PopUpFrame(self, title=_("Error!"), text=text)
            elif self.run_network(cycles):
                self.cycles_completed += cycles

    def continuous_command(self):
        """Run continuous simulation."""
        self.run_network(1)
        self.cycles_completed += 1

    def path_leaf(self, path):
        """Get the filename from a path."""
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def startup_load(self):
        """Handle the loading of a definition file at startup."""
        with wx.FileDialog(
            self, _("Open Definition file"),
            wildcard="Definition files (*.txt)|*.txt",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.pathname = fileDialog.GetPath()

            self.filename = self.path_leaf(self.pathname)

            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(self.pathname, names)
            parser = Parser(names, devices, network, monitors, scanner)
            parser.parse_network()
            error_list = scanner.error_list
            num_errors = len(error_list)

            pages = math.ceil(num_errors/4)

            if num_errors != 0:

                text_list = []
                tab_labels = []

                for i in range(pages-1):
                    tab_labels.append("{}-{}".format(1 + i * 4, 4 + i * 4))
                    label = 4 + i * 4

                if num_errors == 1:
                    tab_labels.append("1")
                elif num_errors <= 4:
                    tab_labels.append("1-{}".format(num_errors))
                else:
                    if (label+1) == num_errors:
                        tab_labels.append("{}".format(num_errors))
                    else:
                        tab_labels.append("{}-{}".format(label+1, num_errors))

                if num_errors == 1:
                    overview = _("\nDefinition file '{}' contains {} error.")\
                        .format(self.filename, num_errors)
                else:
                    overview = _("\nDefinition file '{}' contains {} errors.")\
                        .format(self.filename, num_errors)

                for i in range(pages):
                    if i == 0:
                        text = '\n' + '*'*76 + '\n'
                    else:
                        text = "".format(self.filename, num_errors)
                    for j in range(4):
                        try:
                            text += (error_list[j + i * 4] + "\n")
                        except IndexError:
                            text += ('\n'*8)
                    text_list.append(text)

                frame = DefinitionErrors(self, title=_("Error!"),
                                         text=text_list, tabs=tab_labels,
                                         overview=overview)

                return

        self.current_filename = self.filename
        self.current_pathname = self.pathname
        self.load_new = True
        self.Show(False)
        self.Destroy()
