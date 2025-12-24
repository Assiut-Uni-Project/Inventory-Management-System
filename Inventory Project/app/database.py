from app import conector
import bcrypt  
from mysql.connector import Error
from app.barcode.barcode_manager import generate_barcode


class Admin:
    # Use the connector module for connections
    def connect(self):
        return conector.create_connection()

    def get_category_id(self, category_name):
        conn = self.connect()
        if not conn: return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
            res = cur.fetchone()
            if res: return res[0]
            else:
                cur.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
                conn.commit(); return cur.lastrowid
        except Error: return None
        finally: conector.close_connection(conn)

    def add_product(self, barcode, name, category_name, price, quantity, image_path):
        generate_barcode(barcode)
        conn = self.connect(); 
        if not conn: return
        try:
            cur = conn.cursor()
            cat_id = self.get_category_id(category_name)
            query = "INSERT INTO products (barcode, name, category_id, supplier_id, price, quantity, image_path) VALUES (%s, %s, %s, 1, %s, %s, %s)"
            cur.execute(query, (barcode, name, cat_id, price, quantity, image_path))
            conn.commit()
        except Error as e: raise e
        finally: conector.close_connection(conn)
        

    def update_product(self, pid, name=None, cat=None, price=None, qty=None, img=None):
        conn = self.connect(); 
        if not conn: return
        try:
            cur = conn.cursor()
            if name: cur.execute("UPDATE products SET name=%s WHERE id=%s", (name, pid))
            if cat:
                cid = self.get_category_id(cat)
                cur.execute("UPDATE products SET category_id=%s WHERE id=%s", (cid, pid))
            if price: cur.execute("UPDATE products SET price=%s WHERE id=%s", (price, pid))
            if qty: cur.execute("UPDATE products SET quantity=%s WHERE id=%s", (qty, pid))
            if img: cur.execute("UPDATE products SET image_path=%s WHERE id=%s", (img, pid))
            conn.commit()
        except Error as e: raise e
        finally: conector.close_connection(conn)

    def delete_product(self, pid):
        conn = self.connect(); 
        if not conn: return
        try:
            cur = conn.cursor(); cur.execute("DELETE FROM products WHERE id=%s", (pid,)); conn.commit()
        except Error as e: raise e
        finally: conector.close_connection(conn)
    

    def get_products(self):
       conn = self.connect()
       if not conn: return []

       try:
              cur = conn.cursor()
              cur.execute("SELECT p.id, p.barcode, p.name, c.name AS category, p.price, p.quantity,p.alert_quantity, p.image_path FROM products p JOIN categories c ON p.category_id = c.id")
              result=[]
              for id, barcode, name, category, price, quantity,alert_quantity, image_path in cur.fetchall():
                  if quantity <= alert_quantity:
                      alert_status=True
                  else:
                        alert_status=False
                  result.append((id, barcode, name, category, price, quantity,alert_status, image_path))
                
              return result
       finally:
           conector.close_connection(conn)

#####################################################################################
# Initialize the backend instance
admin_backend = Admin()


#####################################################################################
# Function to add a new user
#####################################################################################
#####################################################################################
    
def add_user(username: str, password: str, role: str) -> tuple[bool, str]:
    #input validation 
    if not username or not password or not role:
        return False, "Username, password, and role cannot be empty."
    if role not in ['admin', 'cashier']:
        return False, "Role must be either 'admin' or 'cashier'."
    if not username.isalnum() and '_' not in username:
        return False, "Username contains invalid characters."
    # Password complexity checks
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/' for char in password):
        return False, "Password must contain at least one special character."
    #store data in database
    hashed_password = hash_password(password)
    connect= None
    cr= None
    try:
        connect= conector.create_connection()
        cr=conector.get_cursor(connect)
        #  Check if username already exists
        check_query = "SELECT username FROM users WHERE username = %s"
        cr.execute(check_query, (username,))  
        existing_user = cr.fetchone() 
        if existing_user:
            return False, "Username already exists."
        # Insert new user
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cr.execute(query, (username, hashed_password, role))
        conector.commit_changes(connect)
        conector.close_connection(connect)
        return True, "User added successfully."
    # Handle any database errors
    except Error as e:
        conector.rollback_changes(connect)
        return False, f"Failed to add user: {e}"
    finally:
        conector.close_connection(connect)

#####################################################################################

#function to change user password
#####################################################################################
#####################################################################################
def change_password (username: str, old_password:str,new_password: str) -> tuple[bool, str]:
    #input validation
    print(f"Changing password for user: {username}")
    # Validate inputs
    if not username or not new_password or not old_password:
        return False, "Username , new password and old password cannot be empty."
    if not username.isalnum() and '_' not in username:
        return False, "Username contains invalid characters."

    connect=None
    cr=None
    try:
        #check old password
        connect= conector.create_connection()
        cr=conector.get_cursor(connect)
        query = "SELECT password FROM users WHERE username = %s"
        cr.execute(query, (username,))
        result = cr.fetchone()
        #check if user exists and old password matches
        if not result:
            return False, "User not found."
        if not compare(old_password, result[0]):
            return False, "Old password is incorrect."
        # check new password complexity
        if len(new_password) < 8:   
            return False, "Password must be at least 8 characters long."    
        if not any(char.isdigit() for char in new_password):
            return False, "Password must contain at least one digit."
        if not any(char.isupper() for char in new_password):
            return False, "Password must contain at least one uppercase letter."
        if not any(char.islower() for char in new_password):
            return False, "Password must contain at least one lowercase letter."
        if not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/' for char in new_password):
            return False, "Password must contain at least one special character."
        #update password in database

        hashed_password = hash_password(new_password)
        query = "UPDATE users SET password = %s WHERE username = %s"
        cr.execute(query, (hashed_password, username))
        conector.commit_changes(connect)
        conector.close_connection(connect)
        return True, "Password changed successfully."
    except Error as e:
        if connect:
            conector.rollback_changes(connect)
        return False, f"Failed to change password: {e}"
    finally:
        if connect:
            conector.close_connection(connect)

######################################################################################
#####################################################################################
#####################################################################################











###########################################################
''' authentecation_and_autherization'''
####################################################
# Function to hash a password
def hash_password(password: str) -> str:
    
    salt = bcrypt.gensalt() # Generate a salt for hashing
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
#####################################################################################
#####################################################################################
# Function to compare a password with a hashed password
#####################################################################################
#####################################################################################
def compare (password: str, hashed: str) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
#####################################################################################
#####################################################################################
# Function to handle user login
#####################################################################################
#####################################################################################
def user_login(username: str, password: str) -> tuple[bool, str, int]:
    # 1. Create connection
    connect = conector.create_connection()
    if not connect:
        return False, "DB Connection Failed", None

    try:
        cr = conector.get_cursor(connect)
        query = "SELECT password,id, role FROM users WHERE username = %s"
        cr.execute(query, (username,))
        result = cr.fetchone()
        
        if result:
            stored_hash = result[0]
            user_id = result[1]
            role = result[2]
            
            if compare(password, stored_hash):
                return True, role, user_id
            else:
                return False, 'Incorrect Password',None       
        return False, 'User not found',None
    except Error as e:
        print(f"Error during login: {e}")
        return False, str(e),None
    finally:
        conector.close_connection(connect)



######################################################################################
#####################################################################################   

'''cashier'''
##################################################################################
#  function validate item for sale
################################################################################
def  validate_item (item_name:str ,itemQuantity:int)->bool:
    ###start connection
    connection= conector.create_connection()
    cr=conector.get_cursor(connection)
    query="SELECT quantity FROM products WHERE name=%s"
    cr.execute( query,(item_name,))
    result=cr.fetchone()
    conector.close_connection(connection)
    #check if item exists and quantity is sufficient
    if result and result[0]>=itemQuantity:
        return True
    else:
        return False
##################################################################################
# add item to cart
##################################################################################
def add_item_to_cart(cart:dict , item_name:str , itemQuantity:int)->dict:
    #validate item
    if not validate_item(item_name,itemQuantity):
        print("Item not valid or insufficient quantity")
        return cart
    #add item to cart
    if item_name not in cart:
        cart[item_name]=0
    cart[item_name]+=itemQuantity
    return cart

##################################################################################
# remove item from cart
##################################################################################
def remove_item_from_cart(cart:dict , item_name:str , itemQuantity:int)->dict:
    if item_name in cart:
        cart[item_name]-=itemQuantity
        if cart[item_name]<=0:
            del cart[item_name]
    return cart

##################################################################################
# calculate total and create sales make receipt
##################################################################################

def calculate_total(cart:dict , cashier_id:int)->float:
    total=0.0
    #start connection
    connection= None
    cr= None
    try:
        connection= conector.create_connection()
        cr=conector.get_cursor(connection)
        # 1-calculate total price first to create Sale Header
        list_recipt=[]
        for item_name,itemQuantity in cart.items():
          query="SELECT id, price FROM products WHERE name=%s"
          cr.execute(query,(item_name,))
          result=cr.fetchone()
          if result:
            product_id = result[0] 
            price=float(result[1])
            list_recipt.append((product_id,item_name, itemQuantity, price))
            total+=price*itemQuantity
        #2-create Sale Header
        insert_total_sales_query="INSERT INTO sales (cashier_id, total_amount) VALUES (%s, %s)"
        cr.execute(insert_total_sales_query,(cashier_id,total))
        #3- id of sale just created
        sale_id=cr.lastrowid
        #4-create Sale Items
        for product_id,item_name,itemQuantity,price in list_recipt:
            insert_sale_items_query="INSERT INTO sale_items (sale_id, product_id,product_name, quantity, price) VALUES (%s, %s, %s, %s, %s)"
            cr.execute(insert_sale_items_query,(sale_id, product_id,item_name, itemQuantity, price))
        
        #commit all changes
        conector.commit_changes(connection)
        return total
    except Error as e:
        print(f"Error during transaction: {e}")
        conector.rollback_changes(connection)
        return 0.0  
    finally:
        # close connection
        conector.close_connection(connection)

####################
# gets total price of cart
##################################################################################
def get_cart_total(cart:dict)->float:
    total=0.0
    #start connection
    connection= conector.create_connection()
    cr=conector.get_cursor(connection)
    for item_name,itemQuantity in cart.items():
        query="SELECT price FROM products WHERE name=%s"
        cr.execute(query,(item_name,))
        result=cr.fetchone()
        if result:
            price=float(result[0])
            total+=price*itemQuantity
    conector.close_connection(connection)
    return total
##################################################################################
#item_price function to get price of item
def item_price(item_name:str)->float:
    price=0.0

    #start connection
    connection= conector.create_connection()
    cr=conector.get_cursor(connection)
    query="SELECT price FROM products WHERE name=%s"
    cr.execute(query,(item_name,))
    result=cr.fetchone()
    conector.close_connection(connection)
    
    if result:
        price=float(result[0])
    return price
##############################################################################
#function to search items
##################################################################################
def search_item(item_name:str)->list:
    #start connection
    connection= None
    cr= None
    try :
         connection= conector.create_connection()
         cr=conector.get_cursor(connection)
         query="SELECT p.id, p.barcode, p.name, c.name AS category, p.price, p.quantity,p.alert_quantity,p.image_path FROM products p JOIN categories c ON p.category_id = c.id WHERE p.name LIKE %s"
         cr.execute(query,(f"%{item_name}%",))
         results=cr.fetchall()
         return results
    except Error as e:
            print(f"Error during search: {e}")
            return []
    finally:
            conector.close_connection(connection)
##################################################################################
# scan item function to scan item by barcode
##########################################
def scan_item(barcode: str) -> tuple[bool, list | str]:    
    #start connection
    connection= None
    cr= None
    try :
         connection= conector.create_connection()
         cr=conector.get_cursor(connection)
         query="SELECT p.id, p.barcode, p.name, c.name AS category, p.price, p.quantity,p.alert_quantity,p.image_path FROM products p JOIN categories c ON p.category_id = c.id WHERE p.barcode=%s"
         cr.execute(query,(barcode,))
         result=cr.fetchone()
         if result:
             return True, result
         else:
             return False, "Item not found"
    except Error as e:
            print(f"Error during scan: {e}")
            return False, str(e)
    finally:
            conector.close_connection(connection)
##################################################################################



