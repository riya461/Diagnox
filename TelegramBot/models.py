from keras.models import load_model
import numpy as np 
from PIL import Image
drAlz = load_model("alzheimers_detection_model.h5")



# Define a function to make predictions on an image
def predict_on_image(image_path):
    # Load and preprocess the image
    img = Image.open(image_path)
    img = img.resize((128, 128))  # Resize the image to match the input size of the model
    x = np.array(img)
    x = x.reshape(1, 128, 128, 3)  # Reshape the image to match the input shape of the model

    # Make predictions
    predictions = drAlz.predict(x)

    # Get the predicted class
    predicted_class = np.argmax(predictions)

    # Get the confidence score for the predicted class
    confidence_score = predictions[0][predicted_class]

    return predicted_class, confidence_score

# Define a function to get the class name based on the predicted class index
def get_class_name(class_index):
    class_names = ['Non Demented', 'Mild Dementia', 'Moderate Dementia', 'Very Mild Dementia']
    return class_names[class_index]
def run():
# Path to the image you want to make predictions on
    image_path = "./uploads/upload.jpg"
    # Make predictions on the image
    predicted_class, confidence_score = predict_on_image(image_path)
    # Get the class name based on the predicted class index
    class_name = get_class_name(predicted_class)
    print(class_name)
    return class_name
    # Print the predicted class and confidence score

run()