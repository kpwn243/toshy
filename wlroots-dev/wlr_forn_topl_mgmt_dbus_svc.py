#!/usr/bin/env python3

print("(--) Starting D-Bus service to monitor wlr-foreign-toplevel-management protocol...")

import os
import sys
import dbus
import time
import signal
import platform
import dbus.service
import dbus.mainloop.glib
import xwaykeyz.lib.logger

from pywayland.client import Display
from gi.repository import GLib
from dbus.exceptions import DBusException
from subprocess import DEVNULL
from typing import Dict
from xwaykeyz.lib.logger import debug, error

xwaykeyz.lib.logger.VERBOSE = True


# Independent module/script to create a D-Bus window context service in 
# a wlroots Wayland environment, which will be notified of window 
# focus changes by the Wayland compositor, as long as the compositor 
# implements the `wlr_foreign_toplevel_management_unstable_v1` protocol.

# Add paths to avoid errors like ModuleNotFoundError or ImportError
home_dir            = os.path.expanduser("~")
run_tmp_dir         = os.environ.get('XDG_RUNTIME_DIR') or '/tmp'
parent_folder_path  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
current_folder_path = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, current_folder_path)
sys.path.insert(0, parent_folder_path)

existing_path = os.environ.get('PYTHONPATH', '')
os.environ['PYTHONPATH'] = f'{parent_folder_path}:{current_folder_path}:{existing_path}'

# local imports now that path is prepped
import lib.env as env

from .protocols.wlr_foreign_toplevel_management_unstable_v1.zwlr_foreign_toplevel_manager_v1 import (
    ZwlrForeignToplevelManagerV1,
    ZwlrForeignToplevelManagerV1Proxy,
    ZwlrForeignToplevelHandleV1
)

if os.name == 'posix' and os.geteuid() == 0:
    error("This app should not be run as root/superuser.")
    sys.exit(1)


def signal_handler(sig, frame):
    """handle signals like Ctrl+C"""
    if sig in (signal.SIGINT, signal.SIGQUIT):
        # Perform any cleanup code here before exiting
        # traceback.print_stack(frame)
        debug(f'\nSIGINT or SIGQUIT received. Exiting.\n')
        # sys.exit(0)
        clean_shutdown()


def clean_shutdown():
    if display:  # Check if the display is globally defined and initialized
        try:
            display.disconnect()
        except Exception as e:
            error(f"Error disconnecting display: {e}")
    GLib.MainLoop().quit()  # Stop the GLib main loop if it's running
    sys.exit(0)


if platform.system() != 'Windows':
    signal.signal(signal.SIGINT,    signal_handler)
    signal.signal(signal.SIGQUIT,   signal_handler)
else:
    error(f'This is only meant to run on Linux. Exiting...')
    sys.exit(1)


sep_reps        = 80
sep_char        = '='
separator       = sep_char * sep_reps

LOG_PFX = 'TOSHY_WLR_DBUS_SVC'

DISTRO_ID       = None
DISTRO_VER      = None
VARIANT_ID      = None
SESSION_TYPE    = None
DESKTOP_ENV     = None
DE_MAJ_VER      = None


def check_environment():
    """Retrieve the current environment from env module"""
    env_info: Dict[str, str] = env.get_env_info()   # Returns a dict
    global DISTRO_ID, DISTRO_VER, VARIANT_ID, SESSION_TYPE, DESKTOP_ENV, DE_MAJ_VER
    DISTRO_ID       = env_info.get('DISTRO_ID')
    DISTRO_VER      = env_info.get('DISTRO_VER')
    VARIANT_ID      = env_info.get('VARIANT_ID')
    SESSION_TYPE    = env_info.get('SESSION_TYPE')
    DESKTOP_ENV     = env_info.get('DESKTOP_ENV')
    DE_MAJ_VER      = env_info.get('DE_MAJ_VER')


check_environment()

# TODO: put the DE restriction back in place, find a way to identify wlroots compositors
if SESSION_TYPE == 'wayland': # and DESKTOP_ENV not in ['kde', 'plasma', 'gnome', 'cinnamon']:
    pass
else:
    debug(f'{LOG_PFX}: Probably not a wlroots environment. Exiting.')
    time.sleep(2)
    sys.exit(0)


debug("")
debug(  f'Toshy KDE D-Bus service script sees this environment:'
        f'\n\t{DISTRO_ID        = }'
        f'\n\t{DISTRO_VER       = }'
        f'\n\t{VARIANT_ID       = }'
        f'\n\t{SESSION_TYPE     = }'
        f'\n\t{DESKTOP_ENV      = }'
        f'\n\t{DE_MAJ_VER       = }\n', ctx="CG")


TOSHY_WLR_DBUS_SVC_PATH         = '/org/toshy/Wlroots'
TOSHY_WLR_DBUS_SVC_IFACE        = 'org.toshy.Wlroots'

wdw_handles_dct                 = {}
active_app_id                   = "NO_WLR_DATA"
active_title                    = "NO_WLR_DATA"

try:
    display = Display()
    display.connect()  # Explicitly attempt to connect to the Wayland display
    registry = display.get_registry()  # Attempt to get the registry
except ValueError as e:  # ValueError is raised if connection fails in your Display class
    print(f"Failed to connect to the Wayland display: {e}")
except RuntimeError as e:  # Catching potential runtime errors, adjust exceptions as needed
    print(f"Runtime error occurred: {e}")
except Exception as e:  # Generic catch-all for any other exceptions
    print(f"An unexpected error occurred: {e}")
else:
    print("Connection to Wayland display and registry acquisition successful.")
    # Proceed with further operations, such as setting up listeners on the registry

toplevel_manager                = None


def handle_app_id_change(handle, app_id):
    if handle not in wdw_handles_dct:
        wdw_handles_dct[handle] = {}
    wdw_handles_dct[handle]['title'] = app_id
    print(f"Title updated for window {handle}: '{app_id}'")


def handle_title_change(handle, title):
    """Update title in local state."""
    if handle not in wdw_handles_dct:
        wdw_handles_dct[handle] = {}
    wdw_handles_dct[handle]['title'] = title
    print(f"Title updated for window {handle}: '{title}'")


def handle_toplevel_event(toplevel_mgr):
    # Here, you should set up event listeners for the toplevel
    toplevel_mgr.dispatcher["app_id"]   = handle_app_id_change
    toplevel_mgr.dispatcher["title"]    = handle_title_change


def wayland_event_check():
    # Check for Wayland events
    # display.flush()
    # display.dispatch()
    display.roundtrip()
    return True  # Returning True keeps the callback active


def handle_registry_global(registry, id_, interface_name, version):
    if interface_name == 'zwlr_foreign_toplevel_manager_v1':
        toplevel_manager = registry.bind(id_, ZwlrForeignToplevelManagerV1, version)
        toplevel_manager.dispatcher["toplevel"] = handle_toplevel_event


registry.dispatcher["global"]    = handle_registry_global

display.roundtrip()


class DBUS_Object(dbus.service.Object):
    """Class to handle D-Bus interactions"""
    def __init__(self, session_bus, object_path, interface_name):
        super().__init__(session_bus, object_path)
        self.interface_name     = interface_name
        self.dbus_svc_bus_name  = dbus.service.BusName(interface_name, bus=session_bus)

    @dbus.service.method(TOSHY_WLR_DBUS_SVC_IFACE, out_signature='a{sv}')
    def GetActiveWindow(self):
        debug(f'{LOG_PFX}: GetActiveWindow() called...')
        return {'app_id':           active_app_id,
                'title':            active_title}


def main():

    # Initialize the D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Connect to the session bus
    session_bus = dbus.SessionBus()

    # Create the DBUS_Object
    try:
        DBUS_Object(session_bus, TOSHY_WLR_DBUS_SVC_PATH, TOSHY_WLR_DBUS_SVC_IFACE)
    except DBusException as dbus_error:
        error(f"{LOG_PFX}: Error occurred while creating D-Bus service object:\n\t{dbus_error}")
        sys.exit(1)

    GLib.idle_add(wayland_event_check)

    # Run the main loop
    # dbus.mainloop.glib.DBusGMainLoop().run()
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
    # maybe do this at the end? 
    # if display and display.connected:  # Assuming `connected` is a property indicating the connection status
    #     display.disconnect()
