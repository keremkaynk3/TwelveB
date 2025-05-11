import sqlite3
import wx

class NotionApp(wx.Frame):
    def __init__(self, user_id, *args, **kwargs):
        super(NotionApp, self).__init__(*args, **kwargs)
        self.dark_mode = self.load_dark_mode_state()
        self.init_ui()
        self.conn = sqlite3.connect("registered.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.user_id = user_id  # Oturum açmış kullanıcı ID'si burada saklanıyor

    def init_ui(self):
        self.SetTitle("Welcome to TwelveB")
        self.SetSize((600, 550))  # Pencere boyutunu arttırdık

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = wx.CheckListBox(panel)
        vbox.Add(self.listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=15)

        # Sol panel
        left_panel = wx.Panel(panel)
        left_panel.SetMinSize((200, 200))  # Sol paneli biraz daha büyük yapmak için
        vbox_left = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.CheckListBox(left_panel)
        vbox_left.Add(self.listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        left_panel.SetSizer(vbox_left)
        hbox.Add(left_panel, proportion=1, flag=wx.EXPAND)

        # Sağ panel
        right_panel = wx.Panel(panel)
        right_panel.SetMinSize((200, 200))  # Sağ paneli biraz daha büyük yapmak için
        vbox_right = wx.BoxSizer(wx.VERTICAL)
        self.todo_listbox = wx.CheckListBox(right_panel)
        vbox_right.Add(self.todo_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        right_panel.SetSizer(vbox_right)
        hbox.Add(right_panel, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox, flag=wx.EXPAND | wx.ALL, border=10)

        # Butonları tek bir yatay kutucuk içinde gruplayarak satırı yarı yarıya bölelim
        button_box = wx.BoxSizer(wx.HORIZONTAL)

        prsnl_button = wx.Button(panel, label="BİREYSEL")
        prsnl_button.Bind(wx.EVT_BUTTON, self.on_add)
        button_box.Add(prsnl_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        acdmc = wx.Button(panel, label="KARİYER")
        acdmc.Bind(wx.EVT_BUTTON, self.on_add2)
        button_box.Add(acdmc, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        vbox.Add(button_box, flag=wx.EXPAND | wx.ALL, border=10)

        self.text_ctrl = wx.TextCtrl(panel)
        vbox.Add(self.text_ctrl, flag=wx.EXPAND | wx.ALL, border=10)

        delete_button = wx.Button(panel, label="Sil")
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
        vbox.Add(delete_button, flag=wx.EXPAND | wx.ALL, border=10)

        edit_button = wx.Button(panel, label="Düzenle")
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        vbox.Add(edit_button, flag=wx.EXPAND | wx.ALL, border=10)

        exit_button = wx.Button(panel, label="Hesap Değiştir")
        exit_button.Bind(wx.EVT_BUTTON, self.on_exit)
        vbox.Add(exit_button, flag=wx.EXPAND | wx.ALL, border=10)

        dark_mode_button = wx.Button(panel, label="Dark Mode")
        dark_mode_button.Bind(wx.EVT_BUTTON, self.toggle_dark_mode)
        vbox.Add(dark_mode_button, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check)
        self.Layout()

    def get_current_user_id(self):
        return self.user_id

    def on_add(self, event):
        item = self.text_ctrl.GetValue()
        if item:
            user_id = self.get_current_user_id()  # Kullanıcının ID'sini almak için bir yol bulunmalıdır
            self.add_note(user_id, item)  # Önce veritabanına ekleyin
            self.show_notes()  # Notları tekrar yükleyin
            self.text_ctrl.Clear()

    def on_add2(self, event):
        item = self.text_ctrl.GetValue()
        if item:
            user_id = self.get_current_user_id()  # Kullanıcının ID'sini almak için bir yol bulunmalıdır
            self.add_note2(user_id, item)  # Önce veritabanına ekleyin
            self.show_notes2()  # Notları tekrar yükleyin
            self.text_ctrl.Clear()

    def add_note(self, user_id, note):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO notes (user_id, note) VALUES (?, ?)", (user_id, note))
        self.conn.commit()
        print("Not kaydedildi:", note)

    def add_note2(self, user_id, note2):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO notes2 (user_id, note2) VALUES (?, ?)", (user_id, note2))
        self.conn.commit()
        print("Not kaydedildi:", note2)

    def show_notes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT note, checked FROM notes WHERE user_id=?", (self.user_id,))
        notes = cursor.fetchall()

        self.listbox.Clear()
        for note, checked in notes:
            self.listbox.Append(note)
            if checked:
                self.listbox.Check(self.listbox.GetCount() - 1)

    def show_notes2(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT note2 FROM notes2 WHERE user_id=?", (self.user_id,))
        notes2 = cursor.fetchall()

        self.todo_listbox.Clear()
        for note2 in notes2:
            self.todo_listbox.Append(note2[0])

    def on_edit(self, event):
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            current_note = self.listbox.GetString(selection)
            dialog = wx.TextEntryDialog(self, "Bireysel notunu düzenle:", "Not Düzenleme")
            dialog.SetValue(current_note)  # Varsayılan değeri ayarla
            if dialog.ShowModal() == wx.ID_OK:
                new_note = dialog.GetValue()
                if new_note and new_note != current_note:
                    self.edit_note(current_note, new_note)
                    self.show_notes()
            dialog.Destroy()

    def on_edit2(self, event):
        selection = self.todo_listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            current_note2 = self.todo_listbox.GetString(selection)
            dialog = wx.TextEntryDialog(self, "Akademik notunu düzenle:", "Not Düzenleme")
            dialog.SetValue(current_note2)  # Varsayılan değeri ayarla
            if dialog.ShowModal() == wx.ID_OK:
                new_note2 = dialog.GetValue()
                if new_note2 and new_note2 != current_note2:
                    self.edit_note2(current_note2, new_note2)
                    self.show_notes2()
            dialog.Destroy()

    def edit_note2(self, current_note2, new_note2):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE notes2 SET note2=? WHERE user_id=? AND note2=?", (new_note2, self.user_id, current_note2))
        self.conn.commit()

    def edit_note(self, current_note, new_note):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE notes SET note=? WHERE user_id=? AND note=?", (new_note, self.user_id, current_note))
        self.conn.commit()

    def on_delete(self, event):
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            note = self.listbox.GetString(selection)
            self.delete_note(note)
            self.show_notes()

    def on_delete2(self, event):
        selection = self.todo_listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            note2 = self.todo_listbox.GetString(selection)
            self.delete_note2(note2)
            self.show_notes2()

    def delete_note(self, note):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes WHERE user_id=? AND note=?", (self.user_id, note))
        self.conn.commit()

    def delete_note2(self, note2):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes2 WHERE user_id=? AND note2=?", (self.user_id, note2))
        self.conn.commit()

    def on_exit(self, event):
        self.Close(True)  # Uygulamayı kapat
        app = wx.GetApp()
        login_dialog = LoginDialog(None)
        login_dialog.ShowModal()

    def on_check(self, event):
        index = event.GetInt()
        if index < 0 or index >= self.listbox.GetCount():
            print(f"Geçersiz indeks: {index}")
            return

        note = self.listbox.GetString(index)
        checked = self.listbox.IsChecked(index)

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id=? AND note=?", (self.user_id, note))
        result = cursor.fetchone()

        if result and result[0] > 0:
            cursor.execute("UPDATE notes SET checked=? WHERE user_id=? AND note=?", (int(checked), self.user_id, note))
            self.conn.commit()
            print(f"Updated note '{note}' to {'checked' if checked else 'unchecked'}.")
        else:
            print(f"Note '{note}' not found for user_id {self.user_id}")

    def on_check2(self, event):
        index = event.GetInt()
        if index < 0 or index >= self.todo_listbox.GetCount():
            print(f"Geçersiz indeks: {index}")
            return

        note2 = self.todo_listbox.GetString(index)
        checked = self.todo_listbox.IsChecked(index)

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes2 WHERE user_id=? AND note2=?", (self.user_id, note2))
        result = cursor.fetchone()

        if result and result[0] > 0:
            cursor.execute("UPDATE notes2 SET checked=? WHERE user_id=? AND note2=?",
                           (int(checked), self.user_id, note2))
            self.conn.commit()
            print(f"Updated note '{note2}' to {'checked' if checked else 'unchecked'}.")
        else:
            print(f"Note '{note2}' not found for user_id {self.user_id}")

    def load_dark_mode_state(self):
        try:
            with open("dark_mode.txt", "r") as file:
                return file.read().strip() == "True"
        except FileNotFoundError:
            return False

    def toggle_dark_mode(self, event):
        self.dark_mode = not self.dark_mode
        self.apply_dark_mode()
        self.save_dark_mode_state_to_db()

    def save_dark_mode_state_to_db(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE settings SET dark_mode = ? WHERE id = 1", (int(self.dark_mode),))
        self.conn.commit()

    def apply_dark_mode(self):
        # Dark mode aktifse arayüz renklerini değiştir
        if self.dark_mode:
            self.SetBackgroundColour(wx.Colour(25, 25, 25))  # Arka plan rengini değiştir
            self.listbox.SetBackgroundColour(wx.Colour(25, 25, 25))  # Liste kutusunun arka plan rengini değiştir
            self.listbox.SetForegroundColour(wx.Colour(25, 25, 25))  # Liste kutusunun metin rengini değiştir
            self.todo_listbox.SetBackgroundColour(wx.Colour(25, 25, 25))  # Liste kutusunun arka plan rengini değiştir
            self.todo_listbox.SetForegroundColour(wx.Colour(500, 500, 500))  # Liste kutusunun metin rengini değiştir
        else:
            self.SetBackgroundColour(wx.NullColour)  # Arka plan rengini varsayılana ayarla
            self.listbox.SetBackgroundColour(wx.NullColour)  # Liste kutusunun arka plan rengini varsayılana ayarla
            self.listbox.SetForegroundColour(wx.NullColour)  # Liste kutusunun metin rengini varsayılana ayarla
            self.todo_listbox.SetBackgroundColour(wx.NullColour)  # Liste kutusunun arka plan rengini varsayılana ayarla
            self.todo_listbox.SetForegroundColour(wx.NullColour)
        self.Refresh()  # Arayüzün yenilenmesini sağla


class LoginDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(LoginDialog, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.SetTitle("Giriş Yap")
        self.SetSize((400, 400))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        username_label = wx.StaticText(panel, label="Kullanıcı Adı:")
        vbox.Add(username_label, flag=wx.LEFT | wx.TOP, border=10)
        self.username_textctrl = wx.TextCtrl(panel)
        vbox.Add(self.username_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        password_label = wx.StaticText(panel, label="Şifre:")
        vbox.Add(password_label, flag=wx.LEFT | wx.TOP, border=10)
        self.password_textctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(self.password_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        login_button = wx.Button(panel, label="Giriş Yap")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)
        vbox.Add(login_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        forgot_button = wx.Button(panel, label="Şifremi Unuttum")
        forgot_button.Bind(wx.EVT_BUTTON, self.on_forgot_password)
        vbox.Add(forgot_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        register_button = wx.Button(panel, label="Kayıt Ol")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        vbox.Add(register_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, border=10)

        exit_application_button = wx.Button(panel, label="Uygulamayı Kapat")
        exit_application_button.Bind(wx.EVT_BUTTON, self.on_exit_application)
        vbox.Add(exit_application_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

    def on_exit_application(self, event):
        self.Destroy()  # Uygulama penceresini kapat
        app = wx.GetApp()
        app.ExitMainLoop()  # Uygulamanın çalışmasını durdur

    def on_forgot_password(self, event):
        username = wx.GetTextFromUser("Lütfen kullanıcı adınızı girin:", "Şifremi Unuttum")
        if username:
            conn = sqlite3.connect("registered.db")
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if user:
                wx.MessageBox(f"Şifreniz: {user[0]}", "Şifreniz", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("Kullanıcı adı bulunamadı!", "Hata", wx.OK | wx.ICON_ERROR)

    def on_register(self, event):
        register_dialog = RegisterDialog(None)
        if register_dialog.ShowModal() == wx.ID_OK:
            wx.MessageBox("Kayıt başarıyla tamamlandı! Lütfen giriş yapın.", "Başarılı", wx.OK | wx.ICON_INFORMATION)

    def on_login(self, event):
        def login(username, password):
            conn = sqlite3.connect("registered.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                return user[0]
            else:
                return None

        username = self.username_textctrl.GetValue()
        password = self.password_textctrl.GetValue()
        user_id = login(username, password)
        if user_id is not None:
            app = wx.GetApp()
            app.frame = NotionApp(user_id, None)
            app.frame.show_notes()  # Kullanıcının iş notlarını göster
            app.frame.show_notes2() # Kullanıcının günlük notlarını göster
            app.frame.Show()
            self.Destroy()
        else:
            wx.MessageBox("Kullanıcı adı veya şifre yanlış!", "Hata", wx.OK | wx.ICON_ERROR)
            self.username_textctrl.Clear()
            self.password_textctrl.Clear()


class RegisterDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(RegisterDialog, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.SetTitle("Kayıt Ol")
        self.SetSize((350, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        username_label = wx.StaticText(panel, label="Kullanıcı Adı:")
        vbox.Add(username_label, flag=wx.LEFT | wx.TOP, border=10)
        self.username_textctrl = wx.TextCtrl(panel)
        vbox.Add(self.username_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        password_label = wx.StaticText(panel, label="Şifre:")
        vbox.Add(password_label, flag=wx.LEFT | wx.TOP, border=10)
        self.password_textctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(self.password_textctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        register_button = wx.Button(panel, label="Kayıt Ol")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)
        vbox.Add(register_button, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

    def on_register(self, event):
        username = self.username_textctrl.GetValue()
        password = self.password_textctrl.GetValue()
        if username and password:
            conn = sqlite3.connect("registered.db")  # Veritabanı burada açılıyor
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()  # Veritabanı burada kapanıyor
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox("Kullanıcı adı ve şifre boş bırakılamaz!", "Hata", wx.OK | wx.ICON_ERROR)


if __name__ == "__main__":
    app = wx.App()
    login_dialog = LoginDialog(None)
    login_dialog.ShowModal()
    app.MainLoop()
