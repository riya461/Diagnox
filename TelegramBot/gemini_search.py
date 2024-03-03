import google.generativeai as genai
import PIL.Image

img = PIL.Image.open('uploads/upload.jpg')
genai.configure(api_key='AIzaSyAQVTwJz8HE2A8br7T9FlNnh1YtntR1F-g')

def run(val):
   
    model=genai.GenerativeModel('gemini-pro-vision')
    # response = model.generate_content( ['Extract all text from the given image as it is. If there are partial texts, OCR it and return it also',img] )
    # response = model.generate_content( ["Extract all legible texts  and partial text as it is from the image without auto completion",img] )

    response = model.generate_content([f"You are an advanced brain MRI radiologist assistant, experienced in observing and analysing a given MRI or CT scan image.The image contained is diagnosed with {val}. Return a short desciription of the image and how did you detect them (possible signs of disease present). Provide few checkpoints so that radiologists can cross check using them if they ever want to.Dont show any unecessary texts and cautions. ",img ])

    print(response.text)
    return response.text
