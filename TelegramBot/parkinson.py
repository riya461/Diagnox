from joblib import load
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Define the filename for the saved model
def value():
    model_filename = 'parkinson_model.joblib'

    # Define the scaler
    scaler = MinMaxScaler()

# give input file.txt
    data_file_path = 'uploads/data.txt'
    with open(data_file_path, 'r') as file:
        data_str = file.read()

    # Convert the data string to a dictionary
    data_dict = eval(data_str)

    # Print the loaded dictionary
    print("Loaded Data Dictionary:")
    print(data_dict)

    # just data processing stuff, don't worry
    sample_data = data_dict

    sample_df = pd.DataFrame([sample_data])

    # Extract features and preprocess
    X_sample = sample_df.drop(columns=sample_df.filter(like='status').columns)
    X_sample_scaled = scaler.fit_transform(X_sample)
    # Make sure to add values for all 22 features

    # Load the model
    loaded_model = load(model_filename)

    # Now, use the loaded model to make predictions on the sample data
    loaded_prediction = loaded_model.predict(X_sample_scaled)

    # Print the loaded prediction
    if loaded_prediction[0] == 1:
        value = "Parkinson Not Detected"
    else:
        value = "No Parkinson"
    return value

