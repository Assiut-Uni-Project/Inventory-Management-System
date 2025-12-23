from app.UI.app_window import InventoryApp
import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = InventoryApp()
    
    app.mainloop()
