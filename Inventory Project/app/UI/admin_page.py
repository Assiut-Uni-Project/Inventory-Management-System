import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image 
import os

from app.database import admin_backend, add_user
from app.database import change_password
from app.UI.helpers import load_items_to_frame
from app.backup.backup import gui_create_backup,gui_get_backup_list,gui_restore_by_index

class AdminPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.search_string = None
        self.refresh_job = None
        self.controller = controller
        self.selected_pid = None

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#2A2D2E")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="ADMIN PANEL", font=("Roboto Medium", 24), text_color="white").pack(pady=(50, 30))

        # Button Style
        btn_style = {
            "height": 45, "corner_radius": 25, "fg_color": "#E5E5E5", 
            "text_color": "black", "hover_color": "#D0D0D0",
            "font": ("Segoe UI", 14), "anchor": "w", "padx": 20
        }

        # Load Icons (Optional - safely handles missing files)
        try:
            icon_user = ctk.CTkImage(Image.open("assets/icons/add_user.png"), size=(20, 20))
            icon_pass = ctk.CTkImage(Image.open("assets/icons/password.png"), size=(20, 20))
            icon_out = ctk.CTkImage(Image.open("assets/icons/logout.png"), size=(20, 20))
            icon_backup = ctk.CTkImage(Image.open("assets/icons/backup.png"), size=(20, 20))        
        except:
            icon_user = icon_pass = icon_out = icon_backup= None

        # Add Sidebar Buttons
        ctk.CTkButton(sidebar, text="➕ Manage Users", image=icon_user, command=self.popup_add_user).pack(fill="x", pady=8, padx=20)
        ctk.CTkButton(sidebar, text="🔑 Change Password", image=icon_pass,command=self.popup_change_pass).pack(fill="x", pady=8, padx=20)# still want backend to usecommand=self.popup_change_pass
        # backup button
        ctk.CTkButton(sidebar, text="💾 Backup", image=icon_backup, command=self.create_backup).pack(fill="x", pady=8, padx=20)
        ctk.CTkButton(sidebar, text="♻️ Restore Backup", image=icon_backup, command=self.restore_backup).pack(fill="x", pady=8, padx=20)





        # Logout Button (Red)
        ctk.CTkButton(sidebar, text="Logout", image=icon_out, height=45, corner_radius=25,
                      fg_color="#C0392B", hover_color="#E74C3C", text_color="white",
                      font=("Segoe UI", 14, "bold"), anchor="w", compound="left",
                      command=lambda: controller.show_frame("ClientPage")).pack(side="bottom", pady=(20, 50), padx=20, fill="x")

        #  CONTENT  
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        # --- HEADER ---
        head = ctk.CTkFrame(content, height=50, fg_color="transparent")
        head.pack(fill="x", pady=(0, 10))

        #search bar 
        self.search_entry = ctk.CTkEntry(head, width=250, placeholder_text="Search items...", font=("Arial", 14))
        self.search_entry.pack(side="left", padx=(100, 10))

        #search button
        ctk.CTkButton(head, text="Search", width=80, fg_color="#2A2D2E", 
                       command=lambda: on_search()).pack(side="left")
        
        def on_search():
            self.search_string = self.search_entry.get().strip()
            load_items_to_frame(self.grid_frame, is_admin_view=True ,on_click_callback=self.fill_form, search_string=self.search_string)




        form_card = ctk.CTkFrame(content, fg_color="#F0F0F0", corner_radius=15)
        form_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form_card, text="Product Details", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", padx=25, pady=(20, 5))


        # Input Grid
        grid = ctk.CTkFrame(form_card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        
        # Dictionary to hold entries
        self.entries = {}
        labels = ["Barcode", "Name", "Category", "Price", "Qty", "Image"]
#

#
        
        grid.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        # Action Buttons
        btns = ctk.CTkFrame(form_card, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(20, 25))
        action_style = {"height": 40, "corner_radius": 20, "font": ("Segoe UI", 14, "bold")}

        ctk.CTkButton(btns, text="Add Product", fg_color="#27AE60", hover_color="#2ECC71", command=lambda: self.ops("add"), **action_style).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btns, text="Update", fg_color="#F39C12", hover_color="#F7DC6F", command=lambda: self.ops("upd"), **action_style).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btns, text="Delete", fg_color="#C0392B", hover_color="#E74C3C", command=lambda: self.ops("del"), **action_style).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btns, text="Clear", fg_color="#95A5A6", hover_color="#B0B0B0", command=self.clear_form, **action_style).pack(side="left", padx=5, expand=True, fill="x")

        # --- LIST AREA ---
        ctk.CTkLabel(content, text="Inventory List 📦", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(10, 10))
        self.grid_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        
        
        
                # Refresh Button
        ctk.CTkButton(head, text="Refresh Inventory", command=self.refresh).pack(side = "right",pady=20)


    def refresh(self):

        self.search_string = self.search_entry.get().strip()
        load_items_to_frame(self.grid_frame, is_admin_view=True ,on_click_callback=self.fill_form,search_string=self.search_string)
        self.clear_form()

        if self.refresh_job:
            self.after_cancel(self.refresh_job)
        
        self.refresh_job = self.after(60000, self.refresh) # 1 minute 



    def create_backup(self):
            res , return_string = gui_create_backup()
            if res == True:
              messagebox.showinfo("Success",return_string)
            else:
             messagebox.showerror("Error", return_string)
#

#

    def fill_form(self, item):
        pid, bc, nm, cat, pr, qt, alert_status , im = item
        self.selected_pid = pid
        data = [bc, nm, cat, pr, qt, im]
        for k, v in zip(["barcode", "name", "category", "price", "qty", "image"], data):
            self.entries[k].delete(0,"end"); self.entries[k].insert(0, str(v) if v else "")

    def clear_form(self):
        self.selected_pid = None
        for e in self.entries.values(): e.delete(0,"end")

    def ops(self, op):
        try:
            d = {k: v.get() for k,v in self.entries.items()}
            if op=="add": admin_backend.add_product(d['barcode'], d['name'], d['category'], float(d['price']), int(d['qty']), d['image'])
            elif op=="upd": admin_backend.update_product(self.selected_pid, d['name'], d['category'], float(d['price']), int(d['qty']), d['image'])
            elif op=="del": admin_backend.delete_product(self.selected_pid)
            self.refresh()
        except Exception as Err: messagebox.showerror("Error", str(Err))


    

    def popup_add_user(self):

        

        # 1. Create the window
        win = ctk.CTkToplevel(self)
        win.title("Add User")
        
        # 2. Set the Size
        width = 300
        height = 400

        win.protocol("WM_DELETE_WINDOW", win.destroy)


        self.controller.update_idletasks() # Make sure we get accurate numbers

        x = self.controller.winfo_x() + (self.controller.winfo_width() // 2) - (width // 2)
        y = self.controller.winfo_y() + (self.controller.winfo_height() // 2) - (height // 2)
        
        # Position
        win.geometry(f"{width}x{height}+{x}+{y}")

        win.transient(self.controller) 
        win.grab_set()                 
        win.focus_set()                

        ctk.CTkLabel(win, text="Add User", font=("Arial", 18, "bold")).pack(pady=20)
        
        ctk.CTkLabel(win, text="UserName", font=("Arial", 18, "bold")).pack(pady=(20,0))
        UserName = ctk.CTkEntry(win, placeholder_text="Username")
        UserName.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(win, text="Password", font=("Arial", 18, "bold")).pack(pady=(20,0))
        Password = ctk.CTkEntry(win, placeholder_text="Password", show="*")
        Password.pack(pady=5, padx=20, fill="x")
        
        Role = ctk.CTkComboBox(win, values=["admin", "cashier"])
        Role.set("admin")
        Role.pack(pady=5, padx=20, fill="x")

        def save_newuser():
                state , error = add_user(UserName.get(), Password.get(), Role.get())
                if state:
                    messagebox.showinfo("Success", "User Added")
                    win.destroy()
                else:
                    messagebox.showerror("Error", error)
                


        ctk.CTkButton(win, text="Save User", command= lambda: save_newuser(), fg_color="green").pack(pady=20)


    

    def popup_change_pass(self):

        




        # 1. Create the window
        win = ctk.CTkToplevel(self)
        win.title("Change Password")
        

        win.protocol("WM_DELETE_WINDOW", win.destroy)


        # 2. Set the Size
        width = 300
        height = 500

        self.controller.update_idletasks() # Make sure we get accurate numbers
        # calculating mainpoint 
        x = self.controller.winfo_x() + (self.controller.winfo_width() // 2) - (width // 2)
        y = self.controller.winfo_y() + (self.controller.winfo_height() // 2) - (height // 2)
        
        # Position
        win.geometry(f"{width}x{height}+{x}+{y}")

        win.transient(self.controller) 
        win.grab_set()                 
        win.focus_set()                

        ctk.CTkLabel(win, text="Change Password", font=("Arial", 18, "bold")).pack(pady=20)
        
        ctk.CTkLabel(win, text="Username", font=("Arial", 18, "bold")).pack(pady=(20,0))
        UserName = ctk.CTkEntry(win, placeholder_text="Username")
        UserName.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(win, text="Old Password", font=("Arial", 18, "bold")).pack(pady=(20,0))
        oldPassword = ctk.CTkEntry(win, placeholder_text="Old Password", show="*")
        oldPassword.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(win, text="New Password", font=("Arial", 18, "bold")).pack(pady=(20,0))
        NewPassword = ctk.CTkEntry(win, placeholder_text="New Password", show="*")
        NewPassword.pack(pady=5, padx=20, fill="x")


        def save_newpass():
         state , error = change_password(UserName.get(), oldPassword.get() ,NewPassword.get())
         if state:
                    messagebox.showinfo("Success", "Password Changed")
                    win.destroy()
         else:
                    messagebox.showerror("Error", error)


        ctk.CTkButton(win, text="Save Password", command=lambda: save_newpass(), fg_color="green").pack(pady=20)

        
        




         



    def restore_backup(self):
    # get 5 string from backend and make user click on the wanted backup 
    # 5 buttons with the name of the backup

        win = ctk.CTkToplevel(self)
        win.title("cheose backup to restore")

        win.protocol("WM_DELETE_WINDOW", win.destroy)

        # Size
        width = 400  
        height = 200   


        self.controller.update_idletasks()


        # calculat mainpoint 
        x = self.controller.winfo_x() + (self.controller.winfo_width() // 2) - (width // 2)
        y = self.controller.winfo_y() + (self.controller.winfo_height() // 2) - (height // 2)
        
        # Position
        win.geometry(f"{width}x{height}+{x}+{y}")

        win.transient(self.controller) 
        win.grab_set()                 
        win.focus_set()      

        options = gui_get_backup_list()
        backup_version = ctk.CTkComboBox(win, values= options)

        if options : backup_version.set(options[0])
        else : ("No Backups Available")

        backup_version.pack(pady=(20,10), padx=20, fill="x")

        def restore():
            try:
                gui_restore_by_index(options.index(backup_version.get()))
                messagebox.showinfo("Success", "Backup Restored Successfully")
                win.destroy()
                self.refresh()
            except Exception as Err:
                messagebox.showerror("Error", str(Err))

        ctk.CTkButton(win, text="restore backup", command=restore, fg_color="green").pack(pady=20)

        

            
        

