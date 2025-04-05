from flask import *
from flask_cors import cross_origin , CORS
import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import MinMaxScaler , LabelEncoder
import warnings
warnings.filterwarnings('ignore')
app = Flask(__name__)
CORS(app)
def model_processing(dt):
    o_df = pd.read_csv("data.csv").drop('diabetes',axis=1)
    col = list(pd.read_csv("data.csv").drop('diabetes',axis=1).columns)
    df = pd.DataFrame([dt],columns=col)
    n_df = pd.concat([o_df,df])
    gender = LabelEncoder().fit_transform(n_df.gender)
    smoking = LabelEncoder().fit_transform(n_df.smoking_history)
    n_df['gender'] = gender
    n_df['smoking_history'] = smoking
    scaler = pd.DataFrame(MinMaxScaler().fit_transform(n_df),columns=n_df.columns)
    model = pickle.load(open("model", 'rb'))
    x = np.array(scaler.iloc[-1]).reshape(1, -1)
    pred = model.predict(x)
    df["diabetes"] = pred[0]
    df.to_csv("database.csv", mode="a", index=False, header=False)
    data = {}
    print(pred[0])
    HBA1C_THRESHOLD = 6.5
    GLUCOSE_THRESHOLD = 126
    data["pred"] = pred[0]
    has_high_hba1c = df["HbA1c_level"].iloc[0] >= HBA1C_THRESHOLD
    has_high_glucose = df["blood_glucose_level"].iloc[0] >= GLUCOSE_THRESHOLD
    if pred[0] == 1.0:
        if has_high_hba1c or has_high_glucose:
            if df["age"].iloc[0] <= 18:
                data["type"] = 1  # Type 1 Diabetes (Juvenile Diabetes)
            else:
                data["type"] = 2  # Type 2 Diabetes (Insulin Resistance)
        else:
        # Model predicts diabetes, but lab values are low
            print("Warning: Model predicted diabetes, but HbA1c and glucose are below clinical thresholds.")
            data["type"] = 3  # Borderline/Atypical Diabetes
    else:
        # If not diabetic, assign type 0
        data["type"] = 0
    print(data)
    return data

def smok_condition(x):
    if x == 'no_info':
        return 'No Info'
    elif x == 'not_current':
        return 'not current'
    else:
        return x
@app.route("/")
def index():
    return "GlugoGenius x v2.0 md-97.17-1 (code : mava)"

@cross_origin()
@app.route('/predict', methods=['GET','POST'])
def predict():
    if request.method == 'POST':
        print(request.json)
        data = request.json
        md = [request.json["gender"][0].upper() + request.json["gender"][1::],float(request.json["age"]) ,int(request.json["hypertension"]),int(request.json["heartDisease"]),smok_condition(request.json["smokingHistory"]),float(request.json["bmi"]),float(request.json["hba1c"]),request.json["bloodGlucose"]]

        print(md)
        pred = model_processing(md)
        print(pred)
        return jsonify(pred)
    return jsonify({"error":True})

if __name__ == '__main__':
    app.run(debug=True)
