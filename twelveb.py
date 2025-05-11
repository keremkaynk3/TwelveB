import wx
import sqlite3
import json
from datetime import datetime
import os

class TwelveBApp(wx.Frame):
    def __init__(self, user_id, *args, **kwargs):
        super(TwelveBApp, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.conn = sqlite3.connect("twelveb.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.current_page = None
        self.init_ui()
        self.load_settings()
        self.load_pages()
        self.create_welcome_page()

    def create_welcome_page(self):
        cursor = self.conn.cursor()
        # Check if welcome page already exists
        cursor.execute("SELECT id FROM pages WHERE title='Welcome to TwelveB' AND user_id=?", (self.user_id,))
        if not cursor.fetchone():
            # Create welcome page
            cursor.execute("""
                INSERT INTO pages (user_id, title, content, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.user_id, "Welcome to TwelveB", """
# Welcome to TwelveB! 🎉

## Core Features:

### 1. Page Management
- Create unlimited pages
- Organize pages in a hierarchical structure
- Drag and drop pages to reorganize
- Search through all your pages

### 2. Rich Text Editing
- Format text (bold, italic, underline)
- Create headings and lists
- Add code blocks
- Insert images and links

### 3. Sticky Notes
- Add colorful sticky notes to any page
- Drag and position notes anywhere
- Choose from multiple colors
- Group related notes together

### 4. Organization
- Tag pages for better organization
- Color-code pages and notes
- Create custom categories
- Quick search and filter

### 5. Customization
- Dark/Light mode
- Customizable font sizes
- Multiple themes
- Personal workspace layout

### 6. Security
- Secure login system
- Password recovery with security questions
- User-specific data isolation
- Automatic data saving

### 7. Additional Features
- Export pages to different formats
- Import content from other sources
- Keyboard shortcuts
- Auto-save functionality

## Getting Started:
1. Create a new page using the "+" button
2. Add content using the rich text editor
3. Organize your pages using drag and drop
4. Add sticky notes for quick reminders
5. Customize your workspace in Settings

## Tips:
- Use tags to organize related pages
- Create a hierarchy of pages for better organization
- Use sticky notes for temporary information
- Try different themes to find your perfect workspace

Happy organizing! 🚀
            """, "#f0f8ff", datetime.now(), datetime.now()))
            self.conn.commit()
            self.load_pages()

    def init_ui(self):
        self.SetTitle("TwelveB")
        self.SetSize((1200, 800))

        # Create main splitter window
        self.splitter = wx.SplitterWindow(self)
        
        # Left sidebar for pages
        self.sidebar = wx.Panel(self.splitter)
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Search box
        self.search_ctrl = wx.SearchCtrl(self.sidebar, style=wx.TE_PROCESS_ENTER)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        sidebar_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        # New page button
        new_page_btn = wx.Button(self.sidebar, label="+ New Page")
        new_page_btn.Bind(wx.EVT_BUTTON, self.on_new_page)
        sidebar_sizer.Add(new_page_btn, 0, wx.EXPAND | wx.ALL, 5)
        
        # Pages tree
        self.pages_tree = wx.TreeCtrl(self.sidebar, style=wx.TR_DEFAULT_STYLE | wx.TR_MULTIPLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.root = self.pages_tree.AddRoot("My Pages")
        self.pages_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_page_select)
        sidebar_sizer.Add(self.pages_tree, 1, wx.EXPAND | wx.ALL, 5)
        
        self.sidebar.SetSizer(sidebar_sizer)
        
        # Main content area
        self.content = wx.Panel(self.splitter)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Page title and toolbar
        toolbar = wx.Panel(self.content)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.page_title = wx.TextCtrl(toolbar, style=wx.TE_PROCESS_ENTER)
        self.page_title.Bind(wx.EVT_TEXT_ENTER, self.on_title_change)
        toolbar_sizer.Add(self.page_title, 1, wx.EXPAND | wx.RIGHT, 5)
        
        # Formatting buttons
        bold_btn = wx.Button(toolbar, label="B")
        bold_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        toolbar_sizer.Add(bold_btn, 0, wx.RIGHT, 2)
        
        italic_btn = wx.Button(toolbar, label="I")
        italic_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        toolbar_sizer.Add(italic_btn, 0, wx.RIGHT, 2)
        
        # Add sticky note button to toolbar
        sticky_note_btn = wx.Button(toolbar, label="📝")
        sticky_note_btn.Bind(wx.EVT_BUTTON, self.on_add_sticky_note)
        toolbar_sizer.Add(sticky_note_btn, 0, wx.RIGHT, 2)
        
        toolbar.SetSizer(toolbar_sizer)
        content_sizer.Add(toolbar, 0, wx.EXPAND | wx.ALL, 5)
        
        # Page content
        self.content_text = wx.TextCtrl(self.content, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.content_text.Bind(wx.EVT_TEXT, self.on_content_change)
        content_sizer.Add(self.content_text, 1, wx.EXPAND | wx.ALL, 5)
        
        self.content.SetSizer(content_sizer)
        
        # Set up splitter
        self.splitter.SplitVertically(self.sidebar, self.content)
        self.splitter.SetMinimumPaneSize(200)
        self.splitter.SetSashPosition(250)
        
        # Create menu bar
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        new_page = file_menu.Append(wx.ID_ANY, "New Page", "Create a new page")
        file_menu.AppendSeparator()
        settings = file_menu.Append(wx.ID_ANY, "Settings", "Open settings")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "Exit", "Exit the application")
        menubar.Append(file_menu, "File")
        
        # Edit menu
        edit_menu = wx.Menu()
        undo = edit_menu.Append(wx.ID_UNDO, "Undo", "Undo last action")
        redo = edit_menu.Append(wx.ID_REDO, "Redo", "Redo last action")
        menubar.Append(edit_menu, "Edit")
        
        # View menu
        view_menu = wx.Menu()
        dark_mode = view_menu.Append(wx.ID_ANY, "Dark Mode", "Toggle dark mode", kind=wx.ITEM_CHECK)
        menubar.Append(view_menu, "View")
        
        self.SetMenuBar(menubar)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_new_page, new_page)
        self.Bind(wx.EVT_MENU, self.on_settings, settings)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_dark_mode, dark_mode)
        
        self.Layout()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT dark_mode, font_size, theme FROM settings WHERE user_id=?", (self.user_id,))
        settings = cursor.fetchone()
        
        if settings:
            dark_mode, font_size, theme = settings
            if dark_mode:
                self.apply_dark_mode()
            self.content_text.SetFont(wx.Font(font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

    def load_pages(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, title, parent_id FROM pages 
                WHERE user_id=? ORDER BY created_at
            """, (self.user_id,))
            
            pages = cursor.fetchall()
            self.pages_tree.DeleteAllItems()
            self.root = self.pages_tree.AddRoot("My Pages")
            
            # Create a dictionary to store page items
            page_items = {None: self.root}
            
            for page_id, title, parent_id in pages:
                parent = page_items.get(parent_id, self.root)
                item = self.pages_tree.AppendItem(parent, title)
                page_items[page_id] = item
            
            # Only try to expand if we have the root item
            if self.root.IsOk():
                self.pages_tree.Expand(self.root)
        except Exception as e:
            print(f"Error loading pages: {str(e)}")
            wx.MessageBox(f"Error loading pages: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def on_new_page(self, event):
        dialog = wx.TextEntryDialog(self, "Enter page title:", "New Page")
        if dialog.ShowModal() == wx.ID_OK:
            title = dialog.GetValue()
            if title:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO pages (user_id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (self.user_id, title, datetime.now(), datetime.now()))
                self.conn.commit()
                self.load_pages()
        dialog.Destroy()

    def on_page_select(self, event):
        item = event.GetItem()
        if item and item != self.root:  # Check if item exists and is not root
            title = self.pages_tree.GetItemText(item)
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM pages WHERE title=? AND user_id=?", (title, self.user_id))
            result = cursor.fetchone()
            if result:
                page_id = result[0]
                self.load_page_content(page_id)

    def load_page_content(self, page_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.title, p.content, p.color, 
                   GROUP_CONCAT(sn.id || ',' || sn.content || ',' || sn.color || ',' || sn.position_x || ',' || sn.position_y)
            FROM pages p
            LEFT JOIN sticky_notes sn ON p.id = sn.page_id
            WHERE p.id = ?
            GROUP BY p.id
        """, (page_id,))
        result = cursor.fetchone()
        
        if result:
            self.current_page = page_id
            title, content, page_color, sticky_notes = result
            
            # Set page title and content
            self.page_title.SetValue(title)
            self.content_text.SetValue(content if content else "")
            
            # Set page color
            if page_color:
                self.content.SetBackgroundColour(wx.Colour(page_color))
            
            # Load sticky notes
            if sticky_notes:
                self.load_sticky_notes(sticky_notes)
            
            self.Refresh()

    def on_title_change(self, event):
        if self.current_page:
            new_title = self.page_title.GetValue()
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE pages 
                SET title=?, updated_at=? 
                WHERE id=?
            """, (new_title, datetime.now(), self.current_page))
            self.conn.commit()
            self.load_pages()

    def on_content_change(self, event):
        if self.current_page:
            content = self.content_text.GetValue()
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE pages 
                SET content=?, updated_at=? 
                WHERE id=?
            """, (content, datetime.now(), self.current_page))
            self.conn.commit()

    def on_search(self, event):
        search_term = self.search_ctrl.GetValue().lower()
        if not search_term:
            self.load_pages()
            return
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, content 
            FROM pages 
            WHERE user_id=? AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
        """, (self.user_id, f"%{search_term}%", f"%{search_term}%"))
        
        results = cursor.fetchall()
        self.pages_tree.DeleteAllItems()
        self.root = self.pages_tree.AddRoot("Search Results")
        
        for page_id, title, content in results:
            item = self.pages_tree.AppendItem(self.root, title)
            self.pages_tree.SetItemData(item, page_id)
        
        self.pages_tree.Expand(self.root)

    def on_settings(self, event):
        dialog = SettingsDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

    def on_dark_mode(self, event):
        cursor = self.conn.cursor()
        cursor.execute("SELECT dark_mode FROM settings WHERE user_id=?", (self.user_id,))
        current = cursor.fetchone()
        
        if current:
            new_mode = 0 if current[0] else 1
            cursor.execute("UPDATE settings SET dark_mode=? WHERE user_id=?", (new_mode, self.user_id))
        else:
            cursor.execute("INSERT INTO settings (user_id, dark_mode) VALUES (?, 1)", (self.user_id,))
        
        self.conn.commit()
        self.apply_dark_mode()

    def apply_dark_mode(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT dark_mode FROM settings WHERE user_id=?", (self.user_id,))
        dark_mode = cursor.fetchone()
        
        if dark_mode and dark_mode[0]:
            self.SetBackgroundColour(wx.Colour(25, 25, 25))
            self.content_text.SetBackgroundColour(wx.Colour(25, 25, 25))
            self.content_text.SetForegroundColour(wx.Colour(255, 255, 255))
        else:
            self.SetBackgroundColour(wx.NullColour)
            self.content_text.SetBackgroundColour(wx.NullColour)
            self.content_text.SetForegroundColour(wx.NullColour)
        
        self.Refresh()

    def on_exit(self, event):
        self.Close()

    def on_add_sticky_note(self, event):
        if not self.current_page:
            wx.MessageBox("Please select a page first!", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        dialog = wx.Dialog(self, title="Add Sticky Note", size=(300, 200))
        panel = wx.Panel(dialog)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Content
        content_label = wx.StaticText(panel, label="Note Content:")
        vbox.Add(content_label, 0, wx.ALL, 5)
        content_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(content_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Color selection
        color_label = wx.StaticText(panel, label="Color:")
        vbox.Add(color_label, 0, wx.ALL, 5)
        color_choice = wx.Choice(panel, choices=[
            "Yellow (#ffff00)",
            "Pink (#ffb6c1)",
            "Green (#90ee90)",
            "Blue (#87cefa)",
            "Purple (#d8bfd8)"
        ])
        vbox.Add(color_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(panel, label="Save")
        cancel_button = wx.Button(panel, label="Cancel")
        
        save_button.Bind(wx.EVT_BUTTON, lambda evt: self.save_sticky_note(
            dialog, content_text.GetValue(), color_choice.GetString(color_choice.GetSelection())
        ))
        cancel_button.Bind(wx.EVT_BUTTON, lambda evt: dialog.EndModal(wx.ID_CANCEL))
        
        button_box.Add(save_button, 0, wx.RIGHT, 5)
        button_box.Add(cancel_button, 0)
        vbox.Add(button_box, 0, wx.ALL | wx.CENTER, 5)
        
        panel.SetSizer(vbox)
        dialog.ShowModal()
        dialog.Destroy()

    def save_sticky_note(self, dialog, content, color_str):
        if not content:
            wx.MessageBox("Please enter some content!", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        color = color_str.split("(")[1].strip(")")
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sticky_notes (page_id, content, color, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (self.current_page, content, color, datetime.now(), datetime.now()))
        self.conn.commit()
        dialog.EndModal(wx.ID_OK)
        self.load_page_content(self.current_page)  # Refresh the page to show new note

    def load_sticky_notes(self, sticky_notes_str):
        # Clear existing sticky notes
        for child in self.content.GetChildren():
            if isinstance(child, wx.Panel) and child.GetName() == "sticky_note":
                child.Destroy()
        
        # Create new sticky notes
        for note_data in sticky_notes_str.split(','):
            note_id, content, color, x, y = note_data.split(',')
            self.create_sticky_note(int(note_id), content, color, int(x), int(y))

    def create_sticky_note(self, note_id, content, color, x, y):
        note = wx.Panel(self.content, name="sticky_note")
        note.SetBackgroundColour(wx.Colour(color))
        note.SetPosition((x, y))
        note.SetSize((200, 150))
        
        # Add content
        text = wx.StaticText(note, label=content)
        text.Wrap(180)
        
        # Make note draggable
        note.Bind(wx.EVT_LEFT_DOWN, lambda evt, n=note: self.on_sticky_note_drag_start(evt, n))
        note.Bind(wx.EVT_MOTION, lambda evt, n=note: self.on_sticky_note_drag(evt, n))
        note.Bind(wx.EVT_LEFT_UP, lambda evt, n=note: self.on_sticky_note_drag_end(evt, n))
        
        self.content.Refresh()

    def on_sticky_note_drag_start(self, event, note):
        note.drag_start_pos = event.GetPosition()
        note.CaptureMouse()

    def on_sticky_note_drag(self, event, note):
        if event.Dragging() and note.HasCapture():
            pos = event.GetPosition()
            new_pos = note.ClientToScreen(pos)
            new_pos = self.content.ScreenToClient(new_pos)
            note.Move(new_pos)

    def on_sticky_note_drag_end(self, event, note):
        if note.HasCapture():
            note.ReleaseMouse()
            # Save new position to database
            if self.current_page:
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE sticky_notes 
                    SET position_x=?, position_y=?, updated_at=?
                    WHERE id=?
                """, (note.GetPosition().x, note.GetPosition().y, datetime.now(), note.note_id))
                self.conn.commit()

class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent, title="Settings", size=(300, 200))
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Font size
        font_box = wx.BoxSizer(wx.HORIZONTAL)
        font_label = wx.StaticText(panel, label="Font Size:")
        self.font_spin = wx.SpinCtrl(panel, value="16", min=8, max=72)
        font_box.Add(font_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        font_box.Add(self.font_spin, 0)
        vbox.Add(font_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # Theme selection
        theme_box = wx.BoxSizer(wx.HORIZONTAL)
        theme_label = wx.StaticText(panel, label="Theme:")
        self.theme_choice = wx.Choice(panel, choices=["Default", "Dark", "Light"])
        theme_box.Add(theme_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        theme_box.Add(self.theme_choice, 0)
        vbox.Add(theme_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(panel, label="Save")
        cancel_button = wx.Button(panel, label="Cancel")
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_box.Add(save_button, 0, wx.RIGHT, 5)
        button_box.Add(cancel_button, 0)
        vbox.Add(button_box, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(vbox)

    def on_save(self, event):
        cursor = self.parent.conn.cursor()
        cursor.execute("""
            UPDATE settings 
            SET font_size=?, theme=? 
            WHERE user_id=?
        """, (self.font_spin.GetValue(), self.theme_choice.GetStringSelection(), self.parent.user_id))
        self.parent.conn.commit()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

class LoginDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(LoginDialog, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.SetTitle("Login to TwelveB")
        self.SetSize((400, 300))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Username
        username_label = wx.StaticText(panel, label="Username:")
        vbox.Add(username_label, flag=wx.LEFT | wx.TOP, border=10)
        self.username_textctrl = wx.TextCtrl(panel)
        vbox.Add(self.username_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Password
        password_label = wx.StaticText(panel, label="Password:")
        vbox.Add(password_label, flag=wx.LEFT | wx.TOP, border=10)
        self.password_textctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(self.password_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        
        login_button = wx.Button(panel, label="Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)
        button_box.Add(login_button, 0, wx.RIGHT, 5)
        
        register_button = wx.Button(panel, label="Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        button_box.Add(register_button, 0, wx.RIGHT, 5)
        
        forgot_button = wx.Button(panel, label="Forgot Password")
        forgot_button.Bind(wx.EVT_BUTTON, self.on_forgot_password)
        button_box.Add(forgot_button, 0)
        
        vbox.Add(button_box, flag=wx.ALL | wx.CENTER, border=10)

        panel.SetSizer(vbox)

    def on_login(self, event):
        username = self.username_textctrl.GetValue()
        password = self.password_textctrl.GetValue()
        
        conn = sqlite3.connect("twelveb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            app = wx.GetApp()
            app.frame = TwelveBApp(user[0], None)
            app.frame.Show()
            self.Destroy()
        else:
            wx.MessageBox("Invalid username or password!", "Error", wx.OK | wx.ICON_ERROR)

    def on_register(self, event):
        dialog = RegisterDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            wx.MessageBox("Registration successful! Please login.", "Success", wx.OK | wx.ICON_INFORMATION)
        dialog.Destroy()

    def on_forgot_password(self, event):
        dialog = ForgotPasswordDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

class RegisterDialog(wx.Dialog):
    def __init__(self, parent):
        super(RegisterDialog, self).__init__(parent, title="Register", size=(400, 400))
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Username
        username_label = wx.StaticText(panel, label="Username:")
        vbox.Add(username_label, flag=wx.LEFT | wx.TOP, border=10)
        self.username_textctrl = wx.TextCtrl(panel)
        vbox.Add(self.username_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Password
        password_label = wx.StaticText(panel, label="Password:")
        vbox.Add(password_label, flag=wx.LEFT | wx.TOP, border=10)
        self.password_textctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(self.password_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Security Question
        security_label = wx.StaticText(panel, label="Security Question:")
        vbox.Add(security_label, flag=wx.LEFT | wx.TOP, border=10)
        self.security_question = wx.Choice(panel, choices=[
            "What was your first pet's name?",
            "In which city were you born?",
            "What is your mother's maiden name?",
            "What was your childhood nickname?",
            "What is the name of your favorite teacher?"
        ])
        vbox.Add(self.security_question, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Security Answer
        answer_label = wx.StaticText(panel, label="Answer:")
        vbox.Add(answer_label, flag=wx.LEFT | wx.TOP, border=10)
        self.security_answer = wx.TextCtrl(panel)
        vbox.Add(self.security_answer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Register button
        register_button = wx.Button(panel, label="Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        vbox.Add(register_button, flag=wx.ALL | wx.CENTER, border=10)

        panel.SetSizer(vbox)

    def on_register(self, event):
        username = self.username_textctrl.GetValue()
        password = self.password_textctrl.GetValue()
        security_question = self.security_question.GetString(self.security_question.GetSelection())
        security_answer = self.security_answer.GetValue()

        if not all([username, password, security_question, security_answer]):
            wx.MessageBox("All fields are required!", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("twelveb.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password, security_question, security_answer)
                VALUES (?, ?, ?, ?)
            """, (username, password, security_question, security_answer))
            conn.commit()
            self.EndModal(wx.ID_OK)
        except sqlite3.IntegrityError:
            wx.MessageBox("Username already exists!", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            conn.close()

class ForgotPasswordDialog(wx.Dialog):
    def __init__(self, parent):
        super(ForgotPasswordDialog, self).__init__(parent, title="Forgot Password", size=(400, 300))
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Username
        username_label = wx.StaticText(panel, label="Username:")
        vbox.Add(username_label, flag=wx.LEFT | wx.TOP, border=10)
        self.username_textctrl = wx.TextCtrl(panel)
        vbox.Add(self.username_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Security Question
        self.security_question_label = wx.StaticText(panel, label="")
        vbox.Add(self.security_question_label, flag=wx.LEFT | wx.TOP, border=10)

        # Security Answer
        answer_label = wx.StaticText(panel, label="Answer:")
        vbox.Add(answer_label, flag=wx.LEFT | wx.TOP, border=10)
        self.security_answer = wx.TextCtrl(panel)
        vbox.Add(self.security_answer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        
        verify_button = wx.Button(panel, label="Verify")
        verify_button.Bind(wx.EVT_BUTTON, self.on_verify)
        button_box.Add(verify_button, 0, wx.RIGHT, 5)
        
        cancel_button = wx.Button(panel, label="Cancel")
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_box.Add(cancel_button, 0)
        
        vbox.Add(button_box, flag=wx.ALL | wx.CENTER, border=10)

        panel.SetSizer(vbox)

    def on_verify(self, event):
        username = self.username_textctrl.GetValue()
        answer = self.security_answer.GetValue()

        if not username:
            wx.MessageBox("Please enter your username!", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("twelveb.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT security_question, security_answer, password 
            FROM users 
            WHERE username=?
        """, (username,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            wx.MessageBox("Username not found!", "Error", wx.OK | wx.ICON_ERROR)
            return

        security_question, security_answer, password = result
        self.security_question_label.SetLabel(security_question)

        if answer.lower() == security_answer.lower():
            wx.MessageBox(f"Your password is: {password}", "Password Recovery", wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox("Incorrect answer!", "Error", wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

if __name__ == "__main__":
    app = wx.App()
    login_dialog = LoginDialog(None)
    login_dialog.ShowModal()
    app.MainLoop() 