import psycopg2  
from datetime import datetime
import hashlib
import json 

DB_PARAMS = {
    "host": "localhost",
    "database": "secure_transaction",
    "user": "postgres",
    "password": "0709",
    "port": 5432    
}
def create_hash(transaction_data):
    
    transaction_string = json.dumps(transaction_data, sort_keys=True)
    return hashlib.sha256(transaction_string.encode()).hexdigest()


def log_transaction(transaction_data):
    conn = None
    try:
        required_fields = ["transaction_id", "user_id", "ammount","merchant_id","product_id"]
        if not all(field in transaction_data for field in required_fields):
            raise ValueError("Missing required fields in transaction data")
        
        hash = create_hash(transaction_data) 
        with psycopg2.connect(**DB_PARAMS)  as conn:
            
         with conn.cursor() as cursor:
            query = """
            INSERT INTO transactions (transaction_id, user_id, ammount, transaction_time, merchant_id, hash, product_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query,( 
             transaction_data["transaction_id"],
             transaction_data["user_id"],
             transaction_data["ammount"],
             transaction_data["Transaction_time"],
             transaction_data["merchant_id"],
             hash,
             transaction_data["product_id"]                                 
           )) 
            conn.commit()
        print("Transaction logged successfully")    
    except  Exception as e:
        print(f"Error logging transaction: {e}")
    finally:
        if conn is not None: 
            conn.close()


if __name__ == "__main__":
    transaction_example = {
        "transaction_id": "Mukund_123959",
        "user_id": "user_78960",
        "ammount": 150.50,
        "Transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "merchant_id": "merchant_4656",
        "product_id": "product_1rl23",
    }
    log_transaction(transaction_example)
    AnomilyDetection = {
        "high ammount": 10000.00,
        "rapid transaction": 5,
        }    
        