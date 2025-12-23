import customtkinter as ctk
from app.UI.login_page import LoginPage
from app.UI.admin_page import AdminPage
from app.UI.client_page import ClientPage
from app.UI.cashier_page import CashierPage

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory System")
        self.geometry("1920x1080")
        self.current_user = None
        self.current_user_id = None

        self.container = ctk.CTkFrame(self); self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ClientPage, LoginPage, AdminPage, CashierPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("ClientPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "refresh"): frame.refresh()
