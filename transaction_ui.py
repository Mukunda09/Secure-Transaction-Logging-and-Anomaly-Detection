import tkinter as tk
from tkinter import messagebox
from secure_log import log_transaction  # Reuse your existing secure logging code
from datetime import datetime

class TransactionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Transaction Logger")

        # Labels
        tk.Label(root, text="Transaction ID:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(root, text="User ID:").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(root, text="ammount ($):").grid(row=2, column=0, padx=10, pady=5)
        tk.Label(root, text="Merchant ID:").grid(row=3, column=0, padx=10, pady=5)
        tk.Label(root, text="Product ID:").grid(row=4, column=0, padx=10, pady=5)

        # Entry Fields
        self.transaction_id = tk.Entry(root)
        self.user_id = tk.Entry(root)
        self.ammount = tk.Entry(root)
        self.merchant_id = tk.Entry(root)
        self.product_id = tk.Entry(root)

        self.transaction_id.grid(row=0, column=1, padx=10, pady=5)
        self.user_id.grid(row=1, column=1, padx=10, pady=5)
        self.ammount.grid(row=2, column=1, padx=10, pady=5)
        self.merchant_id.grid(row=3, column=1, padx=10, pady=5)
        self.product_id.grid(row=4, column=1, padx=10, pady=5)

        # Submit Button
        tk.Button(root, text="Submit Transaction", command=self.submit).grid(row=5, column=0, columnspan=2, pady=10)

    def validate_inputs(self):
        """Check for empty fields and valid amount"""
        fields = {
            "Transaction ID": self.transaction_id.get(),
            "User ID": self.user_id.get(),
            "ammount": self.ammount.get(),
            "Merchant ID": self.merchant_id.get(),
            "product_id": self.product_id.get()
        }

        # Check for empty fields
        for field, value in fields.items():
            if not value.strip():
                messagebox.showerror("Error", f"{field} cannot be empty!")
                return False

        # Validate amount is numeric
        try:
            float(fields["ammount"])
        except ValueError:
            messagebox.showerror("Error", "ammount must be a number!")
            return False

        return True

    def submit(self):
        if not self.validate_inputs():
            return

        # Build transaction data
        transaction = {
            "transaction_id": self.transaction_id.get().strip(),
            "user_id": self.user_id.get().strip(),
            "ammount": float(self.ammount.get().strip()),
            "Transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "merchant_id": self.merchant_id.get().strip(),
            "product_id": self.product_id.get().strip()
        }

        try:
            # Log to database (reuse your secure_logger.py function)
            log_transaction(transaction)
            messagebox.showinfo("Success", "Transaction logged securely!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to log transaction: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransactionApp(root)
    root.mainloop()
    
    