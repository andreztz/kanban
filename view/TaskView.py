from model.Task import Task
from .TextEntry import TextEntry,ActivableTextEntry

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject, Pango


class TaskEditDialog(Gtk.Dialog):

    def __init__(self, window, task):
        Gtk.Dialog.__init__(self, "Task edit", window, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.APPLY))

        self.task = task

        self.entry = TextEntry(self.task.title)
        self.entry.connect("modified-cancel", lambda w: self.emit("response", Gtk.ResponseType.CANCEL))
        self.entry.connect("modified-save", self.on_save)

        box = self.get_content_area()
        box.add(self.entry)
        self.show_all()

    def on_save(self, widget):
        self.task.title = self.entry.get_text()
        self.emit("response", Gtk.ResponseType.APPLY)

class TaskView(Gtk.ListBoxRow):

    __gsignals__ = {
        "modified": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "delete": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, task, board):
        super(Gtk.ListBoxRow, self).__init__()
        self.task = task
        self.connect("modified", lambda widget,
                     title: self.task.set_title(title))
        self.buttons = dict()
        self.refresh_layout(self.task)
        self.connect("key-press-event", self.on_key_press)

    def refresh_layout(self, task):
        # Cleanup first
        for child in self.get_children():
            self.remove(child)
        # drag handle
        self.drag_handle = Gtk.EventBox().new()
        self.drag_handle.add(
            Gtk.Image().new_from_icon_name("open-menu-symbolic", 1))
        # entry
        self.label = Gtk.Label(task.title)
        self.label.set_line_wrap(True)
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_xalign(0)
        # buttons
        self.buttons["edit"] = Gtk.Button.new_from_icon_name(
            "document-edit-symbolic", 1)
        self.buttons["edit"].connect("clicked", self.on_edit_clicked)
        self.buttons["edit"].set_can_focus(False)
        self.buttons["delete"] = Gtk.Button.new_from_icon_name(
            "user-trash-full-symbolic", 1)
        self.buttons["delete"].connect("clicked", lambda w: self.emit("delete"))
        self.buttons["delete"].set_can_focus(False)
        buttonsbox = Gtk.Box(spacing=1)
        for name, button in self.buttons.items():
            buttonsbox.pack_start(button, False, False, 0)
        # Add all elements
        self.box = Gtk.Box(spacing=2)
        self.box.pack_start(self.drag_handle, False, False, 5)
        self.box.pack_start(self.label, True, True, 0)
        self.box.pack_end(buttonsbox, False, False, 0)
        self.add(self.box)

    def on_modified(self, widget, title):
        self.emit("modified", title)

    # Edit
    def on_key_press(self, widget, event):
        if widget is not self:
            return
        k = event.keyval
        if k == Gdk.KEY_Return:
            self.buttons["edit"].clicked()
        elif k == Gdk.KEY_Delete:
            self.buttons["delete"].clicked()

    def on_edit_clicked(self, button):
        dialog = TaskEditDialog(self.get_ancestor(Gtk.Window), self.task)
        response = dialog.run()

        if response == Gtk.ResponseType.APPLY:
            self.emit("modified", self.task.title)
            print("The Save button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        print(self.task)

        dialog.destroy()

        self.label.set_text(self.task.title)

        #if self.entry.is_editable():
        #    self.entry.uneditable()
        #else:
        #    self.entry.editable()

