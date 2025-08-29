import json
import sys
import numpy as np
from sklearn.linear_model import LinearRegression

# Simple training data: [followers, engagement_rate, avg_views] -> revenue
TRAIN_X = np.array([
    [10000, 0.02, 2000],
    [50000, 0.05, 10000],
    [200000, 0.04, 50000],
    [1000000, 0.08, 200000],
    [300000, 0.03, 70000]
], dtype=float)
TRAIN_Y = np.array([200, 3000, 8000, 50000, 12000], dtype=float)

MODEL = LinearRegression().fit(TRAIN_X, TRAIN_Y)

def predict(data):
    x = np.array([[data.get('followers', 0),
                   data.get('engagementRate', 0) / 100.0,
                   data.get('avgViews', 0)]])
    return float(MODEL.predict(x)[0])

if __name__ == '__main__':
    payload = sys.stdin.read() or '{}'
    features = json.loads(payload)
    result = predict(features)
    print(json.dumps({'prediction': result}))
