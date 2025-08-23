import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_wifi_data():
    data = []
    now = datetime.now()
    
    for day in range(5):  # 5 days of data
        for minute in range(0, 1440, 2):  # Every 2 minutes
            timestamp = now - timedelta(days=4-day) + timedelta(minutes=minute)
            hour = timestamp.hour
            
            # Base values with daily patterns
            base_rssi = -65 + (-10 if 1 <= hour <= 5 else 0)
            base_noise = 15 + (20 if 18 <= hour <= 22 else 0)
            
            if np.random.random() < 0.7:  # Good connection
                rssi = base_rssi + np.random.normal(0, 3)
                noise = base_noise + np.random.uniform(-5, 5)
                ap_count = np.random.randint(1, 4)
                stability = 1
            else:  # Bad connection
                rssi = base_rssi + np.random.normal(-15, 5)
                noise = base_noise + np.random.uniform(10, 30)
                ap_count = np.random.randint(4, 9)
                stability = 0
                
            data.append([
                timestamp.isoformat(),
                rssi,
                noise,
                rssi - noise,  # SNR
                (ap_count / 11.0) * 100,  # Channel util
                stability
            ])
    
    return pd.DataFrame(data, columns=[
        'timestamp', 'rssi', 'noise', 'snr', 'channel_util', 'stability'
    ])

df = generate_wifi_data()
df.to_csv('wifi_data.csv', index=False)
print("Dataset generated: wifi_data.csv")