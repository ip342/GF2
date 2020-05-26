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

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
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
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text, cycles=10):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(cycles):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
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
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


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

    def __init__(self, title, path, names, devices, network, monitors):
        
        """Initialise variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position
        self.spin_ctrl_1_value = 10
        self.current_cycles = 10
        
        
        
        
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        label_1 = wx.StaticText(self, wx.ID_ANY, "Cycles")
        label_2 = wx.StaticText(self, wx.ID_ANY, "Switch")
        label_3 = wx.StaticText(self, wx.ID_ANY, "Controls")
        label_4 = wx.StaticText(self, wx.ID_ANY, "Monitor")
        self.spin_ctrl_1 = wx.SpinCtrl(self, wx.ID_ANY, "10", min=0, max=100)
        self.choice_1 = wx.Choice(self, wx.ID_ANY, choices=["SW1", "SW2", "SW3"])
        self.choice_2 = wx.Choice(self, wx.ID_ANY, choices=["0", "1"])
        self.choice_3 = wx.Choice(self, wx.ID_ANY, choices=["A", "B", "C"])
        self.button_1 = wx.Button(self, wx.ID_ANY, "Continue")
        self.button_2 = wx.Button(self, wx.ID_ANY, "Run")
        self.button_3 = wx.Button(self, wx.ID_ANY, "Set")
        self.button_4 = wx.Button(self, wx.ID_ANY, "Set")
        self.button_5 = wx.Button(self, wx.ID_ANY, "Zap")
        
        # Configure the widget properties
        self.SetBackgroundColour(wx.Colour(72, 72, 72))
        label_1.SetForegroundColour(wx.Colour(255, 255, 255))
        label_2.SetForegroundColour(wx.Colour(255, 255, 255))
        label_3.SetForegroundColour(wx.Colour(255, 255, 255))
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

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)
        
        side_sizer.Add(sizer_1, 1, wx.ALL, 0)
        side_sizer.Add(sizer_2, 1, wx.ALL, 5)
        side_sizer.Add(sizer_3, 1, wx.ALL, 0)
        side_sizer.Add(sizer_4, 1, wx.ALL, 10)
        side_sizer.Add(sizer_5, 1, wx.ALL, 0)
        side_sizer.Add(sizer_6, 1, wx.ALL, 10)
        side_sizer.Add(sizer_7, 1, wx.ALL, 0)
        
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

    def on_spin_ctrl_1(self, event):
        """Handle the event when the user changes the spin control 1 value."""
        self.spin_ctrl_1_value = self.spin_ctrl_1.GetValue()
        text = "".join(["New spin control 1 value: ", str(self.spin_ctrl_1_value)])
        self.canvas.render(text, self.current_cycles)
        
    def on_choice_1(self, event):
        """Handle the event when the user changes the choice 1 selection."""
        self.choice_1_selection = self.choice_1.GetCurrentSelection()
        text = "".join(["New choice 1 selection: ", str(self.choice_1_selection)])
        self.canvas.render(text, self.choice_1_selection)
    
    def on_choice_2(self, event):
        """Handle the event when the user changes the choice 2 selection."""
        self.choice_2_selection = self.choice_2.GetCurrentSelection()
        text = "".join(["New choice 2 selection: ", str(self.choice_2_selection)])
        self.canvas.render(text, self.choice_2_selection)
        
    def on_choice_3(self, event):
        """Handle the event when the user changes the choice 3 selection."""
        self.choice_3_selection = self.choice_3.GetCurrentSelection()
        text = "".join(["New choice 3 selection: ", str(self.choice_3_selection)])
        self.canvas.render(text, self.choice_3_selection)

    def on_button_1(self, event):
        """Handle the event when the user clicks button 1."""
        text = "Continue button pressed."
        self.current_cycles = self.spin_ctrl_1_value
        self.canvas.render(text, self.spin_ctrl_1_value)
        self.continue_command()

    def on_button_2(self, event):
        """Handle the event when the user clicks button 2."""
        text = "Run button pressed."
        self.current_cycles = self.spin_ctrl_1_value
        self.canvas.render(text, self.spin_ctrl_1_value)
        self.run_command()
        
    def on_button_3(self, event):
        """Handle the event when the user clicks button 3."""
        text = "Run button pressed."
        self.canvas.render(text, self.spin_value)
        self.run_command()
        
    def on_button_4(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text, self.spin_value)
        self.run_command()
        
    def on_button_5(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text, self.spin_value)
        self.run_command()

    # def on_text_box(self, event):
    #     """Handle the event when the user enters text."""
    #     text_box_value = self.text_box.GetValue()
    #     text = "".join(["New text box value: ", text_box_value])
    #     self.canvas.render(text, self.spin_value)
        
    # def command_interface(self):
    #     """Read the command entered and call the corresponding function."""
    #     print("Logic Simulator: interactive command line user interface.\n"
    #           "Enter 'h' for help.")
    #     self.get_line()  # get the user entry
    #     command = self.read_command()  # read the first character
    #     while command != "q":
    #         if command == "h":
    #             self.help_command()
    #         elif command == "s":
    #             self.switch_command()
    #         elif command == "m":
    #             self.monitor_command()
    #         elif command == "z":
    #             self.zap_command()
    #         elif command == "r":
    #             self.run_command()
    #         elif command == "c":
    #             self.continue_command()
    #         else:
    #             print("Invalid command. Enter 'h' for help.")
    #         self.get_line()  # get the user entry
    #         command = self.read_command()  # read the first character
    #
    # def get_line(self):
    #     """Print prompt for the user and update the user entry."""
    #     self.cursor = 0
    #     self.line = input("#: ")
    #     while self.line == "":  # if the user enters a blank line
    #         self.line = input("#: ")
    #
    # def read_command(self):
    #     """Return the first non-whitespace character."""
    #     self.skip_spaces()
    #     return self.character
    #
    # def get_character(self):
    #     """Move the cursor forward by one character in the user entry."""
    #     if self.cursor < len(self.line):
    #         self.character = self.line[self.cursor]
    #         self.cursor += 1
    #     else:  # end of the line
    #         self.character = ""
    #
    # def skip_spaces(self):
    #     """Skip whitespace until a non-whitespace character is reached."""
    #     self.get_character()
    #     while self.character.isspace():
    #         self.get_character()
    #
    # def read_string(self):
    #     """Return the next alphanumeric string."""
    #     self.skip_spaces()
    #     name_string = ""
    #     if not self.character.isalpha():  # the string must start with a letter
    #         print("Error! Expected a name.")
    #         return None
    #     while self.character.isalnum():
    #         name_string = "".join([name_string, self.character])
    #         self.get_character()
    #     return name_string
    #
    # def read_name(self):
    #     """Return the name ID of the current string if valid.
    #
    #     Return None if the current string is not a valid name string.
    #     """
    #     name_string = self.read_string()
    #     if name_string is None:
    #         return None
    #     else:
    #         name_id = self.names.query(name_string)
    #     if name_id is None:
    #         print("Error! Unknown name.")
    #     return name_id
    #
    # def read_signal_name(self):
    #     """Return the device and port IDs of the current signal name.
    #
    #     Return None if either is invalid.
    #     """
    #     device_id = self.read_name()
    #     if device_id is None:
    #         return None
    #     elif self.character == ".":
    #         port_id = self.read_name()
    #         if port_id is None:
    #             return None
    #     else:
    #         port_id = None
    #     return [device_id, port_id]
    #
    # def read_number(self, lower_bound, upper_bound):
    #     """Return the current number.
    #
    #     Return None if no number is provided or if it falls outside the valid
    #     range.
    #     """
    #     self.skip_spaces()
    #     number_string = ""
    #     if not self.character.isdigit():
    #         print("Error! Expected a number.")
    #         return None
    #     while self.character.isdigit():
    #         number_string = "".join([number_string, self.character])
    #         self.get_character()
    #     number = int(number_string)
    #
    #     if upper_bound is not None:
    #         if number > upper_bound:
    #             print("Number out of range.")
    #             return None
    #
    #     if lower_bound is not None:
    #         if number < lower_bound:
    #             print("Number out of range.")
    #             return None
    #
    #     return number
    #
    # def help_command(self):
    #     """Print a list of valid commands."""
    #     print("User commands:")
    #     print("r N       - run the simulation for N cycles")
    #     print("c N       - continue the simulation for N cycles")
    #     print("s X N     - set switch X to N (0 or 1)")
    #     print("m X       - set a monitor on signal X")
    #     print("z X       - zap the monitor on signal X")
    #     print("h         - help (this command)")
    #     print("q         - quit the program")
    #
    # def switch_command(self):
    #     """Set the specified switch to the specified signal level."""
    #     switch_id = self.read_name()
    #     if switch_id is not None:
    #         switch_state = self.read_number(0, 1)
    #         if switch_state is not None:
    #             if self.devices.set_switch(switch_id, switch_state):
    #                 print("Successfully set switch.")
    #             else:
    #                 print("Error! Invalid switch.")
    #
    # def monitor_command(self):
    #     """Set the specified monitor."""
    #     monitor = self.read_signal_name()
    #     if monitor is not None:
    #         [device, port] = monitor
    #         monitor_error = self.monitors.make_monitor(device, port,
    #                                                    self.cycles_completed)
    #         if monitor_error == self.monitors.NO_ERROR:
    #             print("Successfully made monitor.")
    #         else:
    #             print("Error! Could not make monitor.")
    #
    # def zap_command(self):
    #     """Remove the specified monitor."""
    #     monitor = self.read_signal_name()
    #     if monitor is not None:
    #         [device, port] = monitor
    #         if self.monitors.remove_monitor(device, port):
    #             print("Successfully zapped monitor")
    #         else:
    #             print("Error! Could not zap monitor.")
    #
    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                # print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True
   
    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        # cycles = self.read_number(0, None)
        cycles = self.spin_ctrl_1_value

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            # print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        # cycles = self.read_number(0, None)
        cycles = self.spin_ctrl_1_value
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
    
    def display_signals(self):
        """Display the signal trace(s) in the text console."""
        # margin = self.get_margin()
        for device_id, output_id in self.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            name_length = len(monitor_name)
            signal_list = self.monitors_dictionary[(device_id, output_id)]
            # print(monitor_name + (margin - name_length) * " ", end=": ")
#             for signal in signal_list:
#                 if signal == self.devices.HIGH:
#                     print("-", end="")
#                 if signal == self.devices.LOW:
#                     print("_", end="")
#                 if signal == self.devices.RISING:
#                     print("/", end="")
#                 if signal == self.devices.FALLING:
#                     print("\\", end="")
#                 if signal == self.devices.BLANK:
#                     print(" ", end="")
#             print("\n", end="")
    


    def TemporaryThingSoICanUseClassAttributesInParser(self):
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.scanner = Scanner(self.input_text.GetValue(), self.names, True)
        self.parser = Parser(self.names, self.devices, self.network, self.monitors, self.scanner)
        