import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("900x550")
app.title("Inventory Management System")

# ---------------------- GLOBAL STATE ----------------------
selected_role = None   # "admin" / "cashier"


# ---------------------- FRAME SWITCHER ----------------------
def show_frame(frame):
    for f in (role_frame, login_frame, client_frame):
        f.pack_forget()
    frame.pack(fill="both", expand=True)



#back_end-----------------

def user_login(username, password):
    import sqlite3 as sql

    dp = sql.connect('database.db')
    cr = dp.cursor()

    cr.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cr.fetchone()

    dp.close()

    if result and result[0] == password:
        return True
    else: return 0


#---------------



# ---------------------- LOGIN LOGIC ----------------------
def handle_login(email_entry, password_entry):
    email = email_entry.get()
    password = password_entry.get()

    if user_login(email, password)== True:
        messagebox.showinfo("Login Success", "Welcome")
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")


# =============================================================
# PAGE 1 — ROLE SELECTION
# =============================================================
role_frame = ctk.CTkFrame(app)

title = ctk.CTkLabel(role_frame, text="Select Your Role",
                     font=ctk.CTkFont(size=26, weight="bold"))
title.pack(pady=30)

def select_role(role):
    global selected_role
    selected_role = role
    update_login_ui()
    show_frame(login_frame)

btn_admin = ctk.CTkButton(role_frame, text="Admin", width=250,
                          command=lambda: select_role("admin"))
btn_cashier = ctk.CTkButton(role_frame, text="Cashier", width=250,
                            command=lambda: select_role("cashier"))
btn_client = ctk.CTkButton(role_frame, text="Customer", width=250,
                           command=lambda: show_frame(client_frame))

btn_admin.pack(pady=10)
btn_cashier.pack(pady=10)
btn_client.pack(pady=10)


# =============================================================
# PAGE 2 — FANCY LOGIN PAGE
# =============================================================
login_frame = ctk.CTkFrame(app)

# Outer card container
main_card = ctk.CTkFrame(login_frame, corner_radius=20)
main_card.pack(expand=True, fill="both", padx=40, pady=40)

# Left Panel
left_panel = ctk.CTkFrame(main_card, fg_color=("#99ccff"))
left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)

left_text = ctk.CTkLabel(left_panel,
                         text="Inventory\nManagement\nSystem",
                         font=ctk.CTkFont(size=36, weight="bold"),
                         text_color="white")
left_text.place(relx=0.5, rely=0.5, anchor="center")

# Right Panel — Login
right_panel = ctk.CTkFrame(main_card, corner_radius=15)
right_panel.pack(side="right", fill="both", padx=40, pady=20)

login_title = ctk.CTkLabel(right_panel, text="Login",
                           font=ctk.CTkFont(size=24, weight="bold"))
login_subtitle = ctk.CTkLabel(right_panel, text="Sign in to continue",
                              font=ctk.CTkFont(size=14))

login_title.pack(pady=(30, 5))
login_subtitle.pack(pady=(0, 20))

# Email
email_label = ctk.CTkLabel(right_panel, text="Email")
email_label.pack(anchor="w", padx=30)
email_entry = ctk.CTkEntry(right_panel, width=280, placeholder_text="Enter your email")
email_entry.pack(padx=30, pady=5)

# Password
password_label = ctk.CTkLabel(right_panel, text="Password")
password_label.pack(anchor="w", padx=30, pady=(10, 0))
password_entry = ctk.CTkEntry(right_panel, width=280, placeholder_text="Enter password", show="•")
password_entry.pack(padx=30, pady=5)

# Login Button
login_btn = ctk.CTkButton(right_panel, text="Sign In", width=280,
                          command=lambda: handle_login(email_entry, password_entry))
login_btn.pack(padx=30, pady=20)

# Back Button
back_btn = ctk.CTkButton(right_panel, text="Back", width=280,
                         fg_color="gray", hover_color="#777",
                         command=lambda: show_frame(role_frame))
back_btn.pack(padx=30)

# Dynamic login title update
def update_login_ui():
    if selected_role == "admin":
        login_title.configure(text="Admin Login")
        login_subtitle.configure(text="Sign in as Administrator")
    else:
        login_title.configure(text="Cashier Login")
        login_subtitle.configure(text="Sign in as Cashier")
    email_entry.delete(0, "end")
    password_entry.delete(0, "end")


# =============================================================
# PAGE 3 — CLIENT VIEW PAGE
# =============================================================
client_frame = ctk.CTkFrame(app)

client_title = ctk.CTkLabel(client_frame, text="Client Product View",
                            font=ctk.CTkFont(size=28, weight="bold"))
client_title.pack(pady=20)

info = ctk.CTkLabel(client_frame,
                    text="Here the customer can view products only.",
                    font=ctk.CTkFont(size=15))
info.pack(pady=10)

btn_back_client = ctk.CTkButton(client_frame, text="Back",
                                fg_color="gray", hover_color="#777",
                                command=lambda: show_frame(role_frame))
btn_back_client.pack(pady=20)


# ---------------- START APP ----------------
show_frame(role_frame)
app.mainloop()