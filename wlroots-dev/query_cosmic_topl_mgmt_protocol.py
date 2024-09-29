#!/usr/bin/env python3


# Reference for generating the protocol modules with pywayland scanner:
# https://github.com/flacjacket/pywayland/issues/8#issuecomment-987040284

# Protocol documentation (original on which COSMIC variant is based):
# https://wayland.app/protocols/wlr-foreign-toplevel-management-unstable-v1

# COSMIC protocol specification XML files:
# https://github.com/pop-os/cosmic-protocols/blob/main/unstable/cosmic-toplevel-info-unstable-v1.xml
# https://github.com/pop-os/cosmic-protocols/blob/main/unstable/cosmic-workspace-unstable-v1.xml

# pywayland method had a NotImplementedError for NewId argument,
# but PR #64 was merged. 


import sys
import select
import signal
import traceback

# COSMIC-specific protocol module, using their own namespace
# XML files downloaded from `cosmic-protocols` GitHub repo, in 'unstable' folder
from protocols.cosmic_toplevel_info_unstable_v1.zcosmic_toplevel_info_v1 import (
    ZcosmicToplevelInfoV1,
    ZcosmicToplevelInfoV1Proxy,
    ZcosmicToplevelHandleV1
)

# # COSMIC protocol update has shifted to involving 'ext_foreign_toplevel_list_v1' interface.
from protocols.ext_foreign_toplevel_list_v1.ext_foreign_toplevel_list_v1 import (
    ExtForeignToplevelListV1,
    ExtForeignToplevelListV1Proxy,
    ExtForeignToplevelHandleV1
)

from pywayland.client import Display
from time import sleep

ERR_NO_WLR_APP_CLASS = "ERR_no_cosmic_app_class"
ERR_NO_WLR_WDW_TITLE = "ERR_no_cosmic_wdw_title"

class WaylandClient:
    def __init__(self):
        """Initialize the WaylandClient."""
        signal.signal(signal.SIGINT, self.signal_handler)
        self.display                            = None
        self.wl_fd                              = None
        self.registry                           = None
        self.forn_topl_mgr_prot_supported       = False
        self.protocol_version                   = None
        self.cosmic_toplvl_mgr                   = None
        self.foreign_toplvl_mgr               = None

        self.wdw_handles_dct                    = {}
        self.active_app_class                   = ERR_NO_WLR_APP_CLASS
        self.active_wdw_title                   = ERR_NO_WLR_WDW_TITLE

    def signal_handler(self, signal, frame):
        print(f"\nSignal {signal} received, shutting down.")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        if self.display is not None:
            print("Disconnecting from Wayland display...")
            self.display.disconnect()
            print("Disconnected from Wayland display.")

    def handle_title_change(self, handle, title):
        """Update title in local state."""
        if handle not in self.wdw_handles_dct:
            self.wdw_handles_dct[handle] = {}
        self.wdw_handles_dct[handle]['title'] = title
        # print(f"Title updated for window {handle}: '{title}'")

    def handle_app_id_change(self, handle, app_id):
        """Update app_id in local state."""
        if handle not in self.wdw_handles_dct:
            self.wdw_handles_dct[handle] = {}
        self.wdw_handles_dct[handle]['app_id'] = app_id
        # print(f"App ID updated for window {handle}: '{app_id}'")

    def handle_window_closed(self, handle):
        """Remove window from local state."""
        if handle in self.wdw_handles_dct:
            del self.wdw_handles_dct[handle]
        print(f"Window {handle} has been closed.")

    def handle_state_change(self, handle, states_bytes):
        """Track active window based on state changes."""
        states = []
        if isinstance(states_bytes, bytes):
            states = list(states_bytes)
        if ZcosmicToplevelHandleV1.state.activated.value in states:
        # if ExtForeignToplevelHandleV1.state.activated.value in states:
            self.active_app_class = self.wdw_handles_dct[handle]['app_id']
            self.active_wdw_title = self.wdw_handles_dct[handle]['title']
            print()
            print(f"Active app class: '{self.active_app_class}'")
            print(f"Active window title: '{self.active_wdw_title}'")
            self.print_running_applications()  # Print the list of running applications

    def print_running_applications(self):
        """Print a complete list of running applications."""
        print("\nList of running applications:")
        print(f"{'App ID':<30} {'Title':<50}")
        print("-" * 80)
        for handle, info in self.wdw_handles_dct.items():
            app_id = info.get('app_id', ERR_NO_WLR_APP_CLASS)
            title = info.get('title', ERR_NO_WLR_WDW_TITLE)
            print(f"{app_id:<30} {title:<50}")
        print()

    def handle_toplevel_event_v1(self, 
            toplevel_manager: ZcosmicToplevelInfoV1Proxy, 
            toplevel_handle: ZcosmicToplevelHandleV1):
            # toplevel_manager: ExtForeignToplevelListV1Proxy, 
            # toplevel_handle: ExtForeignToplevelHandleV1):
        """Handle events for new toplevel windows in v1 protocol."""
        # print(f"New toplevel window created: {toplevel_handle}")
        # Subscribe to title and app_id changes as well as close event
        toplevel_handle.dispatcher['title']             = self.handle_title_change
        toplevel_handle.dispatcher['app_id']            = self.handle_app_id_change
        toplevel_handle.dispatcher['closed']            = self.handle_window_closed
        toplevel_handle.dispatcher['state']             = self.handle_state_change

    def handle_toplevel_event_v2(self,
                foreign_toplvl_mgr: ExtForeignToplevelListV1Proxy,
                foreign_toplvl_handle: ExtForeignToplevelHandleV1):
        """Send a request to get a cosmic toplevel handle from a foreign toplevel handle."""
        try:

            # # Need to create a new ID for the cosmic_toplevel?
            # # This causes an AttributeError for 'display' not having this attribute:
            # cosmic_toplevel_id = self.display.create_resource_id(ZcosmicToplevelHandleV1)

            # cosmic_toplevel_handle = self.cosmic_toplvl_mgr.get_cosmic_toplevel(
            #                                 cosmic_toplevel_id, foreign_toplevel_handle)
            cosmic_toplvl_handle = self.cosmic_toplvl_mgr.get_cosmic_toplevel(foreign_toplvl_handle)

            # Set up event listeners for the new cosmic_toplevel_handle
            cosmic_toplvl_handle.dispatcher['title']      = self.handle_title_change
            cosmic_toplvl_handle.dispatcher['app_id']     = self.handle_app_id_change
            cosmic_toplvl_handle.dispatcher['closed']     = self.handle_window_closed
            cosmic_toplvl_handle.dispatcher['state']      = self.handle_state_change

            # # Keep track of this handle
            # self.wdw_handles_dct[cosmic_toplevel_handle] = {}

        except KeyError as e:
            print(f"Error sending get_cosmic_toplevel request: {e}")

    def registry_global_handler(self, registry, id_, interface_name, version):
        """Handle registry events."""
        print(f"Registry event: id={id_}, interface={interface_name}, version={version}")

        if interface_name == 'ext_foreign_toplevel_list_v1':
            print(f"Subscribing to 'toplevel' events from foreign toplevel manager...")
            self.foreign_toplvl_mgr = registry.bind(id_, ExtForeignToplevelListV1, version)
            self.foreign_toplvl_mgr.dispatcher['toplevel'] = self.handle_toplevel_event_v2

            # Maybe shouldn't do this here, only do when zcosmic interface is bound
            # self.display.roundtrip()

        # COSMIC is using their own namespace instead of 'zwlr_foreign_toplevel_manager_v1'
        if interface_name == 'zcosmic_toplevel_info_v1':
            print()
            print(f"Protocol '{interface_name}' version {version} is _SUPPORTED_.")
            self.forn_topl_mgr_prot_supported       = True
            self.protocol_version                   = version
            print(f"Creating toplevel manager...")

            self.cosmic_toplvl_mgr = registry.bind(id_, ZcosmicToplevelInfoV1, version)

            if version == 1:
                print(f"Subscribing to 'toplevel' events from toplevel manager...")
                self.cosmic_toplvl_mgr.dispatcher['toplevel'] = self.handle_toplevel_event_v1
                print()

            elif version >= 2:
                pass
                # print(f"Subscribing to 'toplevel' events from foreign toplevel manager...")
                # self.foreign_toplvl_mgr = registry.bind(id_, ExtForeignToplevelListV1, version)
                # self.foreign_toplvl_mgr.dispatcher['toplevel'] = self.handle_toplevel_event_v2

            self.display.roundtrip()

    def run(self):
        """Run the Wayland client."""
        try:
            print("Connecting to Wayland display...")
            with Display() as self.display:
                self.display.connect()
                print("Connected to Wayland display")

                self.wl_fd = self.display.get_fd()
                print("Got Wayland file descriptor")

                print("Getting registry...")
                self.registry = self.display.get_registry()
                print("Registry obtained")

                print("Subscribing to 'global' events from registry")
                self.registry.dispatcher["global"] = self.registry_global_handler

                print("Running roundtrip to process registry events...")
                self.display.roundtrip()

                # After initial events are processed, we should know if the right
                # protocol is supported, and have a toplevel_manager object.
                if self.forn_topl_mgr_prot_supported and self.cosmic_toplvl_mgr:
                    print()
                    print("Protocol 'zcosmic_toplevel_info_v1' is supported, starting dispatch loop...")

                    # # Can't get this to stop pegging a core (or thread) without sleep()
                    # # It is as if dispatch() does not block at all
                    # # TODO: Need to properly use a lightweight event-driven loop, but how? 
                    # while self.display.dispatch() != -1:
                    #     sleep(0.05)
                    #     # seems to be necessary to trigger roundtrip() in a loop,
                    #     # or no further events will ever print out in the terminal
                    #     self.display.roundtrip()

                    while True:
                        # Wait for the Wayland file descriptor to be ready
                        rlist, wlist, xlist = select.select([self.wl_fd], [], [])

                        if self.wl_fd in rlist:
                            # self.display.dispatch()   # won't show me new events
                            self.display.roundtrip()

                else:
                    print()
                    print("Protocol 'zcosmic_toplevel_info_v1' is _NOT_ supported.")

        except Exception as e:
            print()
            print(f"An error occurred: {e}")
            print(traceback.format_exc())

if __name__ == "__main__":
    print("Starting Wayland client...")
    client = WaylandClient()
    client.run()
    print("Wayland client finished")
