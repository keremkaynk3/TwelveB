import sys
import traceback
import wx
import sqlite3

try:
    from twelveb import LoginDialog
    
    app = wx.App()
    login_dialog = LoginDialog(None)
    login_dialog.ShowModal()
    app.MainLoop()
except Exception as e:
    print("Error occurred:", str(e))
    print("\nFull traceback:")
    traceback.print_exc()
    
    # Check database connection
    try:
        conn = sqlite3.connect("twelveb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nDatabase tables:", tables)
        conn.close()
    except Exception as db_error:
        print("\nDatabase connection error:", str(db_error))
    
    # Check Python and wxPython versions
    print("\nPython version:", sys.version)
    print("wxPython version:", wx.version()) 