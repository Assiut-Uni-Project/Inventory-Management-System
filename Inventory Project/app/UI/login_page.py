import customtkinter as ctk
from app.database import user_login

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_card = ctk.CTkFrame(self, corner_radius=20)
        main_card.pack(expand=True, fill="both", padx=40, pady=40)

        left = ctk.CTkFrame(main_card, fg_color="#99ccff")
        left.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(left, text="Inventory\nManagement\nSystem", font=("Arial", 36, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        right = ctk.CTkFrame(main_card, corner_radius=15)
        right.pack(side="right", fill="both", padx=40, pady=20)
        ctk.CTkLabel(right, text="Login", font=("Roboto", 30)).pack(pady=(20, 10))
        ctk.CTkLabel(right, text="Username").pack(anchor="w", padx=30)
        
        self.u_entry = ctk.CTkEntry(right, width=280, font=("Segoe UI", 13), placeholder_text="Username") 
        self.u_entry.pack(pady=5, padx=30)
        ctk.CTkLabel(right, text="Password").pack(anchor="w", padx=30)
        self.p_entry = ctk.CTkEntry(right, width=280, font=("Segoe UI", 13), placeholder_text="Password", show="*") 
        self.p_entry.pack( padx=30)
        
        self.err_lbl = ctk.CTkLabel(right, text="", text_color="#e74c3c", font=("Roboto", 12, "bold"),height=20)
        self.err_lbl.pack(pady=(5,0))

        ctk.CTkButton(right, text="Sign In", width=280, font=("Roboto Medium", 14), command=self.handle_login).pack(pady=10)
        ctk.CTkButton(right, text="Back", width=280, fg_color="gray", command=lambda: controller.show_frame("ClientPage")).pack()

    def handle_login(self):
        u, p = self.u_entry.get(), self.p_entry.get()
        self.err_lbl.configure(text="")
        if not u or not p: self.err_lbl.configure(text="Fill all fields"); return

        success, res,user_id = user_login(u, p)
        if success:
            self.u_entry.delete(0, "end")
            self.p_entry.delete(0, "end")
            self.controller.current_user = u
            self.controller.current_user_id = user_id
            if res == "admin": self.controller.show_frame("AdminPage")
            elif res == "cashier": self.controller.show_frame("CashierPage")
        else:
            self.err_lbl.configure(text=f"{res}")
