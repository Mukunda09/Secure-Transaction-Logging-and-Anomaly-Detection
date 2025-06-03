from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from datetime import datetime

# Configuration
DB_URL = 'postgresql://postgres:0709@localhost/secure_transaction'

def detect_anomalies_with_dbscan():
    """Detect anomalies using DBSCAN clustering"""
    try:
        engine = create_engine(DB_URL)
        
        # Load transaction data
        with engine.connect() as conn:
            df = pd.read_sql(
                text("""
                SELECT transaction_id, user_id, ammount, transaction_time, merchant_id
                FROM transactions
                WHERE transaction_time >= NOW() - INTERVAL '30 days'
                """),
                conn
            )
            
        if df.empty:
            print("No transactions found in the last 30 days")
            return False
            
        # Prepare data for clustering (focus on amount and time)
        df['hour_of_day'] = pd.to_datetime(df['transaction_time']).dt.hour
        X = df[['ammount', 'hour_of_day']].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5) 
        clusters = dbscan.fit_predict(X_scaled)
        
        df['is_anomaly'] = clusters == -1
        df['anomaly_reason'] = np.where(
            df['is_anomaly'],
            'Cluster-based anomaly (DBSCAN)',
            None
        )
        
        plt.scatter(X[:, 0], X[:, 1], c=clusters, cmap='viridis')
        plt.xlabel('Amount (standardized)')
        plt.ylabel('Hour of Day (standardized)')
        plt.title('Transaction Clusters (DBSCAN)')
        plt.savefig('transaction_clusters.png')
        plt.close()
        
        with engine.begin() as conn:
            conn.execute(
                text("""
                UPDATE transactions 
                SET is_anomaly = FALSE, 
                    anomaly_reason = NULL
                WHERE anomaly_reason LIKE 'Cluster-based%'
                """)
            )
            
            anomalies = df[df['is_anomaly']]
            if not anomalies.empty:
                for _, row in anomalies.iterrows():
                    conn.execute(
                        text("""
                        UPDATE transactions 
                        SET is_anomaly = TRUE, 
                            anomaly_reason = :reason
                        WHERE transaction_id = :txn_id
                        """),
                        {
                            "reason": f"Cluster-based anomaly (Amount: {row['ammount']}, Hour: {row['hour_of_day']})",
                            "txn_id": row['transaction_id']
                        }
                    )
        
        print(f" DBSCAN detected {len(anomalies)} potential anomalies")
        return True
        
    except Exception as e:
        print(f" Error during DBSCAN detection: {e}")
        return False

def generate_cluster_report():
    """Generate report for cluster-based anomalies"""
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            df = pd.read_sql(
                text("""
                SELECT transaction_id, user_id, ammount, transaction_time, merchant_id, anomaly_reason
                FROM transactions
                WHERE is_anomaly = TRUE AND anomaly_reason LIKE 'Cluster-based%'
                """),
                conn
            )

        if df.empty:
            print("No cluster-based anomalies found.")
            return False

        report_filename = f"cluster_anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("=== CLUSTER-BASED ANOMALY REPORT ===\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            for _, row in df.iterrows():
                f.write(
                    f"🔍 Anomalous Transaction\n"
                    f"ID: {row['transaction_id']}\n"
                    f"User: {row['user_id']}\n"
                    f"Amount: ${row['ammount']:,.2f}\n"
                    f"Time: {row['transaction_time']}\n"
                    f"Reason: {row['anomaly_reason']}\n"
                    f"Merchant: {row['merchant_id']}\n"
                    f"{'-'*50}\n"
                )

        print(f" Cluster report generated: {report_filename}")
        return report_filename

    except Exception as e:
        print(f" Cluster report generation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Running Cluster-Based Anomaly Detection ===")
    if detect_anomalies_with_dbscan():
        generate_cluster_report()