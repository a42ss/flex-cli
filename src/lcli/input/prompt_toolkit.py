from typing import Any, List, Optional, Tuple, TypeVar

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer
from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import D, HSplit, Layout
from prompt_toolkit.layout.containers import AnyContainer
from prompt_toolkit.shortcuts.dialogs import _return_none
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList, TextArea


_T = TypeVar("_T")


class LcliDialog(RadioList):
    def _handle_enter(self):
        super()._handle_enter()
        get_app().exit(result=self.current_value)


class RadioListButtonHandler(object):
    def __init__(self, button: dict, radio_list: RadioList):
        self.radio_list = radio_list
        self.button = button

    def __call__(self, *args, **kwargs) -> None:
        get_app().exit(result=self.button["text"])


def radiolist_dialog(
    title: AnyFormattedText = "",
    text: AnyFormattedText = "",
    values: Optional[List[Tuple[_T, AnyFormattedText]]] = None,
    buttons=None,
    style: Optional[BaseStyle] = None,
) -> Application[_T]:
    """
    Display a simple list of element the user can choose amongst.

    Only one element can be selected at a time using Arrow keys and Enter.
    The focus can be moved between the list and the Ok/Cancel button with tab.
    """
    if buttons is None:
        buttons = {}
    if values is None:
        values = []

    radio_list = LcliDialog(values)

    buttons_list = []
    for key in buttons:
        button = buttons[key]
        handler = RadioListButtonHandler(button, radio_list)
        if "handler" in button:
            handler = button["handler"](button, radio_list)
        button_object = Button(text=button["text"], handler=handler)
        buttons_list.append(button_object)

    dialog = Dialog(
        title=title,
        body=HSplit([Label(text=text, dont_extend_height=True), radio_list], padding=1),
        buttons=buttons_list,
        with_background=True,
    )

    return _create_app(dialog, style)


def input_dialog(
    title: AnyFormattedText = "",
    text: AnyFormattedText = "",
    ok_text: str = "OK",
    cancel_text: str = "Cancel",
    completer: Optional[Completer] = None,
    password: FilterOrBool = False,
    style: Optional[BaseStyle] = None,
) -> Application[str]:
    """
    Display a text input box.
    Return the given text, or None when cancelled.
    """

    def accept(buf: Buffer) -> bool:
        get_app().layout.focus(ok_button)
        return True  # Keep text.

    def ok_handler() -> None:
        get_app().exit(result=textfield.text)

    ok_button = Button(text=ok_text, handler=ok_handler)
    cancel_button = Button(text=cancel_text, handler=_return_none)

    textfield = TextArea(
        multiline=False, password=password, completer=completer, accept_handler=accept
    )

    dialog = Dialog(
        title=title,
        body=HSplit(
            [
                Label(text=text, dont_extend_height=True),
                textfield,
            ],
            padding=D(preferred=1, max=1),
        ),
        buttons=[ok_button, cancel_button],
        with_background=True,
    )

    return _create_app(dialog, style)


def _create_app(dialog: AnyContainer, style: Optional[BaseStyle]) -> Application[Any]:
    # Key bindings.
    bindings = KeyBindings()
    bindings.add("tab")(focus_next)
    bindings.add("s-tab")(focus_previous)

    @bindings.add(Keys.Escape)
    @bindings.add("c-c")
    @bindings.add("c-q")
    def _(event):
        """Pressing Ctrl-Q or Ctrl-C will exit the user interface."""
        event.app.exit()

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings(
            [
                load_key_bindings(),
                bindings,
            ]
        ),
        mouse_support=True,
        style=style,
        full_screen=True,
    )
