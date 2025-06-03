import psycopg2
import hashlib
import json
from datetime import datetime

DB_PARAMS = {
    "host": "localhost",
    "database": "secure_transaction",
    "user": "postgres",
    "password": "0709",  # CHANGE THIS
    "port": "5432"  # Default PostgreSQL port
}

def create_hash(transaction_data):
    """Create SHA-256 hash of transaction data"""
    transaction_str = json.dumps(transaction_data, sort_keys=True)
    return hashlib.sha256(transaction_str.encode()).hexdigest()

def log_transaction(transaction):
    """Securely log a transaction to the database"""
    conn = None
    try:
        # Input validation
        required_fields = ['transaction_id', 'user_id', 'ammount', 'merchant_id']
        if not all(field in transaction for field in required_fields):
            raise ValueError("Missing required fields in transaction")
        
        if not isinstance(transaction['ammount'], (int, float)):
            raise ValueError("Amount must be a number")

        # Create hash
        transaction_hash = create_hash(transaction)
        
        # Connect to database
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Insert with parameterized query
        query = """
        INSERT INTO transactions 
        (transaction_id, user_id, ammount, , merchant_id, hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            transaction['transaction_id'],
            transaction['user_id'],
            transaction['ammount'],
        
            transaction['merchant_id'],
            transaction_hash
        ))
        
        conn.commit()
        print("Transaction logged successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        print("Please check:")
        print("- Is PostgreSQL running?")
        print("- Are the DB_PARAMS correct?")
        print("- Can you connect via pgAdmin?")
        return False
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

# Test function
if __name__ == "__main__":
    test_data = {
        "transaction_id": "test_001",
        "user_id": "user_123",
        "ammount": 100.0,
    
        "merchant_id": "mcht_456"
    }
    
    print("Testing transaction logging...")
    if log_transaction(test_data):
        print("✅ Test transaction succeeded!")
    else:
        print("❌ Test transaction failed")