#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys

import wx
import builtins

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                error_list = scanner.error_list
                for error in error_list:
                    print(error)
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()
            else:
                error_list = scanner.error_list
                for error in error_list:
                    print(error)

    if not options:  # no option given, use the graphical user interface

        path = None
        names = None
        devices = None
        network = None
        monitors = None
        filename = None
        app = wx.App()

        # Internationalisation
        builtins._ = wx.GetTranslation
        locale = wx.Locale()
        locale.Init(wx.LANGUAGE_DEFAULT)
        locale.AddCatalogLookupPathPrefix('./locale')
        locale.AddCatalog('messages')

        gui = Gui(_("பனி Logic Simulator"), path, names, devices, network,
                  monitors, filename, True)
        gui.Show(True)
        gui.startup_load()
        app.MainLoop()

        while gui.load_new is True:
            path = gui.current_pathname
            filename = gui.current_filename
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the gui.Gui() class
                gui = Gui(_("பனி Logic Simulator - {}").format(filename), path,
                          names, devices, network, monitors, filename)
                gui.Show(True)
                app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
