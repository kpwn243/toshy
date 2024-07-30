# This file has been autogenerated by the pywayland scanner

# Copyright © 2008-2011 Kristian Høgsberg
# Copyright © 2010-2011 Intel Corporation
# Copyright © 2012-2013 Collabora, Ltd.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice (including the
# next paragraph) shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import enum

from pywayland.protocol_core import (
    Argument,
    ArgumentType,
    Global,
    Interface,
    Proxy,
    Resource,
)

from .wl_output import WlOutput
from .wl_seat import WlSeat
from .wl_surface import WlSurface


class WlShellSurface(Interface):
    """Desktop-style metadata interface

    An interface that may be implemented by a
    :class:`~pywayland.protocol.wayland.WlSurface`, for implementations that
    provide a desktop-style user interface.

    It provides requests to treat surfaces like toplevel, fullscreen or popup
    windows, move, resize or maximize them, associate metadata like title and
    class, etc.

    On the server side the object is automatically destroyed when the related
    :class:`~pywayland.protocol.wayland.WlSurface` is destroyed. On the client
    side, wl_shell_surface_destroy() must be called before destroying the
    :class:`~pywayland.protocol.wayland.WlSurface` object.
    """

    name = "wl_shell_surface"
    version = 1

    class resize(enum.IntFlag):
        none = 0
        top = 1
        bottom = 2
        left = 4
        top_left = 5
        bottom_left = 6
        right = 8
        top_right = 9
        bottom_right = 10

    class transient(enum.IntFlag):
        inactive = 0x1

    class fullscreen_method(enum.IntEnum):
        default = 0
        scale = 1
        driver = 2
        fill = 3


class WlShellSurfaceProxy(Proxy[WlShellSurface]):
    interface = WlShellSurface

    @WlShellSurface.request(
        Argument(ArgumentType.Uint),
    )
    def pong(self, serial: int) -> None:
        """Respond to a ping event

        A client must respond to a ping event with a pong request or the client
        may be deemed unresponsive.

        :param serial:
            serial number of the ping event
        :type serial:
            `ArgumentType.Uint`
        """
        self._marshal(0, serial)

    @WlShellSurface.request(
        Argument(ArgumentType.Object, interface=WlSeat),
        Argument(ArgumentType.Uint),
    )
    def move(self, seat: WlSeat, serial: int) -> None:
        """Start an interactive move

        Start a pointer-driven move of the surface.

        This request must be used in response to a button press event. The
        server may ignore move requests depending on the state of the surface
        (e.g. fullscreen or maximized).

        :param seat:
            seat whose pointer is used
        :type seat:
            :class:`~pywayland.protocol.wayland.WlSeat`
        :param serial:
            serial number of the implicit grab on the pointer
        :type serial:
            `ArgumentType.Uint`
        """
        self._marshal(1, seat, serial)

    @WlShellSurface.request(
        Argument(ArgumentType.Object, interface=WlSeat),
        Argument(ArgumentType.Uint),
        Argument(ArgumentType.Uint),
    )
    def resize(self, seat: WlSeat, serial: int, edges: int) -> None:
        """Start an interactive resize

        Start a pointer-driven resizing of the surface.

        This request must be used in response to a button press event. The
        server may ignore resize requests depending on the state of the surface
        (e.g. fullscreen or maximized).

        :param seat:
            seat whose pointer is used
        :type seat:
            :class:`~pywayland.protocol.wayland.WlSeat`
        :param serial:
            serial number of the implicit grab on the pointer
        :type serial:
            `ArgumentType.Uint`
        :param edges:
            which edge or corner is being dragged
        :type edges:
            `ArgumentType.Uint`
        """
        self._marshal(2, seat, serial, edges)

    @WlShellSurface.request()
    def set_toplevel(self) -> None:
        """Make the surface a toplevel surface

        Map the surface as a toplevel surface.

        A toplevel surface is not fullscreen, maximized or transient.
        """
        self._marshal(3)

    @WlShellSurface.request(
        Argument(ArgumentType.Object, interface=WlSurface),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Uint),
    )
    def set_transient(self, parent: WlSurface, x: int, y: int, flags: int) -> None:
        """Make the surface a transient surface

        Map the surface relative to an existing surface.

        The x and y arguments specify the location of the upper left corner of
        the surface relative to the upper left corner of the parent surface, in
        surface-local coordinates.

        The flags argument controls details of the transient behaviour.

        :param parent:
            parent surface
        :type parent:
            :class:`~pywayland.protocol.wayland.WlSurface`
        :param x:
            surface-local x coordinate
        :type x:
            `ArgumentType.Int`
        :param y:
            surface-local y coordinate
        :type y:
            `ArgumentType.Int`
        :param flags:
            transient surface behavior
        :type flags:
            `ArgumentType.Uint`
        """
        self._marshal(4, parent, x, y, flags)

    @WlShellSurface.request(
        Argument(ArgumentType.Uint),
        Argument(ArgumentType.Uint),
        Argument(ArgumentType.Object, interface=WlOutput, nullable=True),
    )
    def set_fullscreen(self, method: int, framerate: int, output: WlOutput | None) -> None:
        """Make the surface a fullscreen surface

        Map the surface as a fullscreen surface.

        If an output parameter is given then the surface will be made
        fullscreen on that output. If the client does not specify the output
        then the compositor will apply its policy - usually choosing the output
        on which the surface has the biggest surface area.

        The client may specify a method to resolve a size conflict between the
        output size and the surface size - this is provided through the method
        parameter.

        The framerate parameter is used only when the method is set to
        "driver", to indicate the preferred framerate. A value of 0 indicates
        that the client does not care about framerate.  The framerate is
        specified in mHz, that is framerate of 60000 is 60Hz.

        A method of "scale" or "driver" implies a scaling operation of the
        surface, either via a direct scaling operation or a change of the
        output mode. This will override any kind of output scaling, so that
        mapping a surface with a buffer size equal to the mode can fill the
        screen independent of buffer_scale.

        A method of "fill" means we don't scale up the buffer, however any
        output scale is applied. This means that you may run into an edge case
        where the application maps a buffer with the same size of the output
        mode but buffer_scale 1 (thus making a surface larger than the output).
        In this case it is allowed to downscale the results to fit the screen.

        The compositor must reply to this request with a configure event with
        the dimensions for the output on which the surface will be made
        fullscreen.

        :param method:
            method for resolving size conflict
        :type method:
            `ArgumentType.Uint`
        :param framerate:
            framerate in mHz
        :type framerate:
            `ArgumentType.Uint`
        :param output:
            output on which the surface is to be fullscreen
        :type output:
            :class:`~pywayland.protocol.wayland.WlOutput` or `None`
        """
        self._marshal(5, method, framerate, output)

    @WlShellSurface.request(
        Argument(ArgumentType.Object, interface=WlSeat),
        Argument(ArgumentType.Uint),
        Argument(ArgumentType.Object, interface=WlSurface),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Uint),
    )
    def set_popup(self, seat: WlSeat, serial: int, parent: WlSurface, x: int, y: int, flags: int) -> None:
        """Make the surface a popup surface

        Map the surface as a popup.

        A popup surface is a transient surface with an added pointer grab.

        An existing implicit grab will be changed to owner-events mode, and the
        popup grab will continue after the implicit grab ends (i.e. releasing
        the mouse button does not cause the popup to be unmapped).

        The popup grab continues until the window is destroyed or a mouse
        button is pressed in any other client's window. A click in any of the
        client's surfaces is reported as normal, however, clicks in other
        clients' surfaces will be discarded and trigger the callback.

        The x and y arguments specify the location of the upper left corner of
        the surface relative to the upper left corner of the parent surface, in
        surface-local coordinates.

        :param seat:
            seat whose pointer is used
        :type seat:
            :class:`~pywayland.protocol.wayland.WlSeat`
        :param serial:
            serial number of the implicit grab on the pointer
        :type serial:
            `ArgumentType.Uint`
        :param parent:
            parent surface
        :type parent:
            :class:`~pywayland.protocol.wayland.WlSurface`
        :param x:
            surface-local x coordinate
        :type x:
            `ArgumentType.Int`
        :param y:
            surface-local y coordinate
        :type y:
            `ArgumentType.Int`
        :param flags:
            transient surface behavior
        :type flags:
            `ArgumentType.Uint`
        """
        self._marshal(6, seat, serial, parent, x, y, flags)

    @WlShellSurface.request(
        Argument(ArgumentType.Object, interface=WlOutput, nullable=True),
    )
    def set_maximized(self, output: WlOutput | None) -> None:
        """Make the surface a maximized surface

        Map the surface as a maximized surface.

        If an output parameter is given then the surface will be maximized on
        that output. If the client does not specify the output then the
        compositor will apply its policy - usually choosing the output on which
        the surface has the biggest surface area.

        The compositor will reply with a configure event telling the expected
        new surface size. The operation is completed on the next buffer attach
        to this surface.

        A maximized surface typically fills the entire output it is bound to,
        except for desktop elements such as panels. This is the main difference
        between a maximized shell surface and a fullscreen shell surface.

        The details depend on the compositor implementation.

        :param output:
            output on which the surface is to be maximized
        :type output:
            :class:`~pywayland.protocol.wayland.WlOutput` or `None`
        """
        self._marshal(7, output)

    @WlShellSurface.request(
        Argument(ArgumentType.String),
    )
    def set_title(self, title: str) -> None:
        """Set surface title

        Set a short title for the surface.

        This string may be used to identify the surface in a task bar, window
        list, or other user interface elements provided by the compositor.

        The string must be encoded in UTF-8.

        :param title:
            surface title
        :type title:
            `ArgumentType.String`
        """
        self._marshal(8, title)

    @WlShellSurface.request(
        Argument(ArgumentType.String),
    )
    def set_class(self, class_: str) -> None:
        """Set surface class

        Set a class for the surface.

        The surface class identifies the general class of applications to which
        the surface belongs. A common convention is to use the file name (or
        the full path if it is a non-standard location) of the application's
        .desktop file as the class.

        :param class_:
            surface class
        :type class_:
            `ArgumentType.String`
        """
        self._marshal(9, class_)


class WlShellSurfaceResource(Resource):
    interface = WlShellSurface

    @WlShellSurface.event(
        Argument(ArgumentType.Uint),
    )
    def ping(self, serial: int) -> None:
        """Ping client

        Ping a client to check if it is receiving events and sending requests.
        A client is expected to reply with a pong request.

        :param serial:
            serial number of the ping
        :type serial:
            `ArgumentType.Uint`
        """
        self._post_event(0, serial)

    @WlShellSurface.event(
        Argument(ArgumentType.Uint),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Int),
    )
    def configure(self, edges: int, width: int, height: int) -> None:
        """Suggest resize

        The configure event asks the client to resize its surface.

        The size is a hint, in the sense that the client is free to ignore it
        if it doesn't resize, pick a smaller size (to satisfy aspect ratio or
        resize in steps of NxM pixels).

        The edges parameter provides a hint about how the surface was resized.
        The client may use this information to decide how to adjust its content
        to the new size (e.g. a scrolling area might adjust its content
        position to leave the viewable content unmoved).

        The client is free to dismiss all but the last configure event it
        received.

        The width and height arguments specify the size of the window in
        surface-local coordinates.

        :param edges:
            how the surface was resized
        :type edges:
            `ArgumentType.Uint`
        :param width:
            new width of the surface
        :type width:
            `ArgumentType.Int`
        :param height:
            new height of the surface
        :type height:
            `ArgumentType.Int`
        """
        self._post_event(1, edges, width, height)

    @WlShellSurface.event()
    def popup_done(self) -> None:
        """Popup interaction is done

        The popup_done event is sent out when a popup grab is broken, that is,
        when the user clicks a surface that doesn't belong to the client owning
        the popup surface.
        """
        self._post_event(2)


class WlShellSurfaceGlobal(Global):
    interface = WlShellSurface


WlShellSurface._gen_c()
WlShellSurface.proxy_class = WlShellSurfaceProxy
WlShellSurface.resource_class = WlShellSurfaceResource
WlShellSurface.global_class = WlShellSurfaceGlobal
