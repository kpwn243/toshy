# This file has been autogenerated by the pywayland scanner

# Copyright © 2018 Ilia Bozhinov
# Copyright © 2020 Isaac Freund
# Copyright © 2024 Victoria Brekenfeld
#
# Permission to use, copy, modify, distribute, and sell this
# software and its documentation for any purpose is hereby granted
# without fee, provided that the above copyright notice appear in
# all copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# the copyright holders not be used in advertising or publicity
# pertaining to distribution of the software without specific,
# written prior permission.  The copyright holders make no
# representations about the suitability of this software for any
# purpose.  It is provided "as is" without express or implied
# warranty.
#
# THE COPYRIGHT HOLDERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS, IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
# AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
# ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
# THIS SOFTWARE.

from __future__ import annotations

from pywayland.protocol_core import (
    Argument,
    ArgumentType,
    Global,
    Interface,
    Proxy,
    Resource,
)

from ..ext_foreign_toplevel_list_v1 import ExtForeignToplevelHandleV1
from .zcosmic_toplevel_handle_v1 import ZcosmicToplevelHandleV1


class ZcosmicToplevelInfoV1(Interface):
    """List toplevels and properties thereof

    The purpose of this protocol is to enable clients such as taskbars or docks
    to access a list of opened applications and basic properties thereof.

    It thus extends ext_foreign_toplevel_v1 to provide more information and
    actions on foreign toplevels.
    """

    name = "zcosmic_toplevel_info_v1"
    version = 2


class ZcosmicToplevelInfoV1Proxy(Proxy[ZcosmicToplevelInfoV1]):
    interface = ZcosmicToplevelInfoV1

    @ZcosmicToplevelInfoV1.request()
    def stop(self) -> None:
        """Stop sending events

        This request indicates that the client no longer wishes to receive
        events for new toplevels.  However, the compositor may emit further
        toplevel_created events until the finished event is emitted.

        The client must not send any more requests after this one.

        Note: This request isn't necessary for clients binding version 2 of
        this protocol and will be ignored.
        """
        self._marshal(0)

    @ZcosmicToplevelInfoV1.request(
        Argument(ArgumentType.NewId, interface=ZcosmicToplevelHandleV1),
        Argument(ArgumentType.Object, interface=ExtForeignToplevelHandleV1),
        version=2,
    )
    def get_cosmic_toplevel(self, foreign_toplevel: ExtForeignToplevelHandleV1) -> Proxy[ZcosmicToplevelHandleV1]:
        """Get cosmic toplevel extension object

        Request a
        :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`
        extension object for an existing
        :class:`~pywayland.protocol.ext_foreign_toplevel_list_v1.ExtForeignToplevelHandleV1`.

        All initial properties of the toplevel (states, etc.) will be sent
        immediately after this event via the corresponding events in
        :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`.

        :param foreign_toplevel:
        :type foreign_toplevel:
            :class:`~pywayland.protocol.ext_foreign_toplevel_list_v1.ExtForeignToplevelHandleV1`
        :returns:
            :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`
        """
        cosmic_toplevel = self._marshal_constructor(1, ZcosmicToplevelHandleV1, foreign_toplevel)
        return cosmic_toplevel


class ZcosmicToplevelInfoV1Resource(Resource):
    interface = ZcosmicToplevelInfoV1

    @ZcosmicToplevelInfoV1.event(
        Argument(ArgumentType.NewId, interface=ZcosmicToplevelHandleV1),
    )
    def toplevel(self, toplevel: ZcosmicToplevelHandleV1) -> None:
        """A toplevel has been created

        This event is never emitted for clients binding version 2 of this
        protocol, they should use `get_cosmic_toplevel` instead.

        This event is emitted for clients binding version 1 whenever a new
        toplevel window is created. It is emitted for all toplevels, regardless
        of the app that has created them.

        All initial properties of the toplevel (title, app_id, states, etc.)
        will be sent immediately after this event via the corresponding events
        in
        :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`.

        :param toplevel:
        :type toplevel:
            :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`
        """
        self._post_event(0, toplevel)

    @ZcosmicToplevelInfoV1.event()
    def finished(self) -> None:
        """The compositor has finished with the toplevel manager

        This event indicates that the compositor is done sending events to the
        :class:`ZcosmicToplevelInfoV1`. The server will destroy the object
        immediately after sending this request, so it will become invalid and
        the client should free any resources associated with it.

        Note: This event is emitted immediately after calling `stop` for
        clients binding version 2 of this protocol for backwards compatibility.
        """
        self._post_event(1)

    @ZcosmicToplevelInfoV1.event(version=2)
    def done(self) -> None:
        """All information about active toplevels have been sent

        This event is sent after all changes for currently active
        :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`
        have been sent.

        This allows changes to multiple
        :class:`~pywayland.protocol.cosmic_toplevel_info_unstable_v1.ZcosmicToplevelHandleV1`
        handles and their properties to be seen as atomic, even if they happen
        via multiple events.
        """
        self._post_event(2)


class ZcosmicToplevelInfoV1Global(Global):
    interface = ZcosmicToplevelInfoV1


ZcosmicToplevelInfoV1._gen_c()
ZcosmicToplevelInfoV1.proxy_class = ZcosmicToplevelInfoV1Proxy
ZcosmicToplevelInfoV1.resource_class = ZcosmicToplevelInfoV1Resource
ZcosmicToplevelInfoV1.global_class = ZcosmicToplevelInfoV1Global
