import customtkinter as ctk
from PIL import Image
import os
from app.database import admin_backend
from app.database import search_item



def load_items_to_frame(target_frame, is_admin_view=False, on_click_callback=None,search_string=None):
    # 1 Clear  widgets
    for widget in target_frame.winfo_children():
        widget.destroy()

    # 2 Configure Grid
    target_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    # 3. Fetch Items
    if search_string:
        items = search_item(search_string) # in case of search
    else:
        items = admin_backend.get_products()
    if not items:
        ctk.CTkLabel(target_frame, text="No items found.", text_color="gray", font=("Arial", 16)).grid(row=0, column=0, columnspan=4, pady=20)
        return
    
    # Colors for card backgrounds
    colors = ["#F07857", "#D94F74", "#766BC4", "#F7A856", "#29AB94"]

    # --- Helper to update card visual state ---
    def update_card_style(card, is_hovering):
        if is_hovering:
            card.configure(border_width=2, border_color="#E0E0E0")
        else:
            card.configure(border_width=0)

    # 4. Create Product Cards
    for index, item in enumerate(items):
        pid, barcode, name, cat, price, qty, alert_status , img_path = item
        
        row_pos = index // 4
        col_pos = index % 4
        bg_color = colors[index % len(colors)]

        # --- Card ---
        card = ctk.CTkFrame(target_frame, fg_color=bg_color, corner_radius=10, height=140)
        card.grid(row=row_pos, column=col_pos, padx=10, pady=10, sticky="ew")
        card.grid_propagate(False) 

        # Grid 
        card.grid_columnconfigure(0, weight=0) # Icon column
        card.grid_columnconfigure(1, weight=1) # Text column


        # Image
        try:
            if img_path and os.path.exists(img_path):
                pil_img = Image.open(img_path)
                my_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
                lbl_icon = ctk.CTkLabel(card, text="", image=my_image)
            else:
                lbl_icon = ctk.CTkLabel(card, text="📦", font=("Arial", 40), text_color="white")
        except Exception:
            lbl_icon = ctk.CTkLabel(card, text="📦", font=("Arial", 40), text_color="white")
            
        lbl_icon.grid(row=0, column=0, rowspan=2, padx=(15, 5), pady=10)


        #Text 
        
        display_name = name 
        lbl_name = ctk.CTkLabel(card, text=display_name, font=("Arial", 16, "bold"), text_color="white", anchor="w")
        lbl_name.grid(row=0, column=1, padx=(0, 10), pady=(15, 0), sticky="sw")


        lbl_value = ctk.CTkLabel(card, text=f"Qty: {qty} | ${price}", font=("Arial", 12, "bold"), text_color="white", anchor="w")
        lbl_value.grid(row=1, column=1, padx=(0, 10), pady=(0, 15), sticky="nw")


        # low stock alert
        if alert_status == 1 and is_admin_view:
            lbl_name.configure(text=f"{display_name} ⚠️", text_color="#DFDFDF")
            lbl_value.configure(text=f"Qty: {qty} ⚠️ | ${price}",text_color="#E2E1E0")



        
        def on_enter(e, c=card): 
            update_card_style(c, True)
            
        def on_leave(e, c=card): 
            update_card_style(c, False)

        def on_click_handler(e, data=item):
            if on_click_callback:
                on_click_callback(data)

        
        widgets_to_bind = [card, lbl_icon, lbl_name, lbl_value]
        for w in widgets_to_bind:
            if is_admin_view or on_click_callback:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click_handler)


