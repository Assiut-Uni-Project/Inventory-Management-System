import customtkinter as ctk
from tkinter import messagebox, simpledialog
from app.UI.helpers import load_items_to_frame
from app.database import admin_backend, add_item_to_cart, remove_item_from_cart, calculate_total
from app.database import item_price, get_cart_total,scan_item
from tkinter import messagebox, filedialog
from app.barcode.barcode_manager import read_barcode_from_image



class CashierPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.search_string = None
        self.refresh_job = None

        self.controller = controller
        
        # --- Variables to hold cart data ---
        self.cart = {} # Dictionary: {item_name: quantity}
        
        # --- Layout Configuration ---
        self.grid_columnconfigure(1, weight=1) # Main content expands
        self.grid_rowconfigure(0, weight=1)


        

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    

        # --- HEADER ---
        head = ctk.CTkFrame(content, height=80, fg_color="transparent")
        head.pack(fill="x", pady=(0, 20))

         # Logout Button
        ctk.CTkButton(head , text="Logout", fg_color="#C0392B", 
        command=lambda: controller.show_frame("LoginPage")).pack( side="left", padx=10)

        # #search bar 
        self.search_entry = ctk.CTkEntry(head, width=250, placeholder_text="Search items...", font=("Arial", 14))
        self.search_entry.pack( side="left", padx=(200,10))

         #search button
        ctk.CTkButton(head, text="Search", width=80, fg_color="#2A2D2E", 
                        command=lambda: on_search()).pack( side="left", padx=(10,10))
        ctk.CTkButton(head, text="⟳", width=40,text_color="#2A2D2E",command=self.refresh).pack(side="right", pady=10)        

        # scan Button
        ctk.CTkButton(head, text="📷 Scan Item",fg_color="#27AE60" ,command=lambda: scan_item_button()).pack(side = "left",pady=10 ,padx=(50,0))
        
        def on_search():
            self.search_string = self.search_entry.get().strip()
            load_items_to_frame(self.grid_frame, is_admin_view=True ,on_click_callback=self.fill_form, search_string=self.search_string)

        #products
        product_frame = ctk.CTkFrame(content, fg_color="transparent")
        product_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))



        ctk.CTkLabel(product_frame, text=" Items : ", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 10))
        
        

        def scan_item_button():
            image_path = filedialog.askopenfilename(title="Select Barcode Image",
                                         filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
            if not image_path:
                return
            
            barcodes = read_barcode_from_image(image_path)
            if not barcodes:
                messagebox.showerror("Error", "No barcode found in the image.")
                return
            state , item = scan_item(barcodes[0]) 
            if state:
                self.add_item_popup(item)
            else:
                messagebox.showerror("Error", "Item not found.")

            
            



        # Scrollable frame for products
        self.grid_frame = ctk.CTkScrollableFrame(product_frame, fg_color="white")
        self.grid_frame.pack(fill="both", expand=True)

        # Refresh Button
        

        cart_panel = ctk.CTkFrame(content, width=300, fg_color="#F0F0F0", corner_radius=10)
        cart_panel.pack(side="right", fill="y", padx=(10, 0))
        
        ctk.CTkLabel(cart_panel, text="receipt", font=("Arial", 18, "bold")).pack(pady=15)
        
        # receipt area
        self.cart_frame = ctk.CTkScrollableFrame(cart_panel, fg_color="transparent")
        self.cart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        #  receipt footer
        self.footer_frame = ctk.CTkFrame(cart_panel, fg_color="transparent")
        self.footer_frame.pack(fill="x", side="bottom", padx=10, pady=20)
        
        # Total Price Label
        self.total_label = ctk.CTkLabel(self.footer_frame, text="Total: $0.00", font=("Arial", 20, "bold"), text_color="#27AE60")
        self.total_label.pack(side="left", padx=10)
        
        # Checkout Button
        self.checkout_btn = ctk.CTkButton(self.footer_frame, text="Checkout", fg_color="#27AE60", width=100, command=self.checkout)
        self.checkout_btn.pack(side="right")

    def refresh(self):
        self.search_string = self.search_entry.get().strip()
        load_items_to_frame(self.grid_frame, is_admin_view=False ,on_click_callback=self.add_item_popup,search_string=self.search_string)
       
        if self.refresh_job:
            self.after_cancel(self.refresh_job)
        
        self.refresh_job = self.after(60000, self.refresh) # 1 minute 

    def add_item_popup(self, item_data):
        name = item_data[2] # [pid, barcode, name, cat, price, qty, img]
        
        qty_str = simpledialog.askstring("Add Item", f"Enter Quantity for {name}:")
        if not qty_str: return 
        
        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError("Quantity must be positive")
            

            self.cart = add_item_to_cart(self.cart, name, qty)
            self.update_cart_display()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    

    def remove_item(self, item_name):
        """Removes item from cart using database logic."""
        if item_name in self.cart:
            qty_to_remove = self.cart[item_name]
            self.cart = remove_item_from_cart(self.cart, item_name, qty_to_remove)
            self.update_cart_display()

    def update_cart_display(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
            
        local_total = get_cart_total(self.cart)
        
        conn = admin_backend.connect()
        
        try:
            for name, qty in self.cart.items():

                
                subtotal = item_price(name) * qty
                
                
                # Row
                row = ctk.CTkFrame(self.cart_frame, fg_color="#E0E0E0", height=40)
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=f"{name} (x{qty})", font=("Arial", 12)).pack(side="left", padx=10)

                ctk.CTkButton(row, text="X", width=30, height=20, fg_color="#C0392B", 
                              command=lambda n=name: self.remove_item(n)).pack(side="right", padx=5, pady=5)
                
                ctk.CTkLabel(row, text=f"${subtotal:.2f}", font=("Arial", 12, "bold")).pack(side="right", padx=10)
        finally:
            if conn: conn.close()

        self.total_label.configure(text=f"Total: ${local_total:.2f}")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty", "Cart is empty")
            return

        self.checkout_btn.configure(state="disabled")

        if not messagebox.askyesno("Confirm", f"Process sale for {self.total_label.cget('text')}?"):
            self.checkout_btn.configure(state="normal")
            return
        
        try:
            total_processed = calculate_total(self.cart, self.controller.current_user_id)
            
            if total_processed > 0:
                messagebox.showinfo("Success", f"Transaction Complete! Total: ${total_processed:.2f}")
                self.cart.clear()
                self.update_cart_display()
                self.refresh() # Reload inventory to show updated stock
            else:
                messagebox.showerror("Error", "Transaction failed (Total 0 or Error).")
                
        except Exception as e:
            messagebox.showerror("Error", f"Transaction Failed: {e}")
        finally:
            self.checkout_btn.configure(state="normal")
