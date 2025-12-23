import customtkinter as ctk
from app.UI.helpers import load_items_to_frame

class ClientPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.refresh_job = None
        self.search_string = None
        self.controller = controller
        
        # main fram of the page
        head = ctk.CTkFrame(self, height=80, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(head, text="Inventory Overview", font=("Roboto Medium", 28), text_color="#333").pack(side="left")
    
        #search bar 
        self.search_entry = ctk.CTkEntry(head, width=250, placeholder_text="Search items...", font=("Arial", 14))
        self.search_entry.pack(side="left", padx=(100, 10))

        #search button
        ctk.CTkButton(head, text="Search", width=80, fg_color="#2A2D2E", 
                       command=lambda: on_search()).pack(side="left")
        


        def on_search():
            self.search_string = self.search_entry.get().strip()
            load_items_to_frame(self.grid_frame, is_admin_view=False, on_click_callback=None, search_string=self.search_string)
 
        # Login Button
        ctk.CTkButton(head, text="Staff Login", width=120, fg_color="#2A2D2E", 
                      command=lambda: controller.show_frame("LoginPage")).pack(side="right", padx=10)
        

        # Gray bar 
        table_header = ctk.CTkFrame(self, height=40, fg_color="#F0F0F0", corner_radius=8)
        table_header.pack(fill="x", padx=30, pady=(10, 0))
        
        # Refresh Button
        ctk.CTkButton(table_header, text="Refresh ", command=self.refresh).pack(side = "left",pady=5, padx=10)        



        # --- SCROLLABLE LIST ---
        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self):
        self.search_string = self.search_entry.get().strip()
        load_items_to_frame(self.grid_frame, is_admin_view=False, on_click_callback=None, search_string = self.search_string )

        if self.refresh_job:
            self.after_cancel(self.refresh_job)
        
        self.refresh_job = self.after(60000, self.refresh) # 1 minute 
