from app import conector
import bcrypt  
from mysql.connector import Error


#####


#####








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

    print("search_item called with:", repr(item_name))

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
