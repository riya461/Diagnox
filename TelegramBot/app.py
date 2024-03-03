import telebot
from telebot import types
import os
from dotenv import load_dotenv
from supabase import create_client
import gemini_search
import time
import models
from functools import partial
import parkinson
load_dotenv()

local_path = f"uploads/upload.jpg"

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase credentials not found in .env file")

supabase = create_client(url, key)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['patient'])
def handle_exit(message):
    response = supabase.table('patients').select('*').execute()
    bot.send_message(message.chat.id, f"Patient details:")
    for patient in response.data:
        bot.send_message(message.chat.id, f"ID: {patient['id']}, Name: {patient['name']}")

@bot.message_handler(commands=['exit'])
def handle_exit(message):
    bot.send_message(message.chat.id, "Thank you for using the bot. Goodbye!")

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_add_mri = types.InlineKeyboardButton('Add data to an Existing Patient', callback_data='existing')
    button_create_patient = types.InlineKeyboardButton('Create New Patient', callback_data='new')
    keyboard.add(button_add_mri, button_create_patient)
    print("Handling /start command")
    bot.send_message(message.chat.id, "Welcome Doctor... \n Choose an option:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(callback):
    try:
        if callback.message:
            if callback.data == 'existing':
                bot.send_message(callback.message.chat.id, "Enter the patient id")
                bot.register_next_step_handler(callback.message, check_existing_patient)
            elif callback.data == 'new':
                bot.send_message(callback.message.chat.id, "Creating new patient... \n")
                bot.send_message(callback.message.chat.id, "Name of the patient:")
                bot.register_next_step_handler(callback.message, create_new_patient)
        
            elif callback.data == 'proceed':
                handle_proceed_callback(callback)
            
            elif callback.data == 'cancel':
                handle_cancel_callback(callback)
              # Call the new cancel callback function
            elif callback.data == 'al':
                with open('disease.txt', 'w') as f:
                    f.write(f"Alzhemeirs")
                bot.send_message(callback.message.chat.id, "Alzhemeirs")
                upload_mri_alzhemeirs(callback.message)

            elif callback.data == 'bt':
                with open('disease.txt', 'w') as f:
                    f.write(f"Brain Tumor")
                bot.send_message(callback.message.chat.id, "Brain Tumor")
            elif callback.data == 'pk':
                with open('disease.txt', 'w') as f:
                    f.write(f"Parkinsons")
                bot.send_message(callback.message.chat.id, "Parkinsons")
                # upload_txt_parkinsons(callback.message)

    except Exception as e:
        print(f"Error: {e}")

def check_existing_patient(message):
    patient_id = message.text
    patient_exists = check_patient_exists_in_database(patient_id)

    if patient_exists:
        bot.send_message(message.chat.id, f"Patient {patient_id} exists.")
        with open('patient.txt', 'w') as f:
            f.write(f"{patient_id}")
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button_alz = types.InlineKeyboardButton('Alzhemeirs',callback_data='al')
        button_bt = types.InlineKeyboardButton('Brain Tumor', callback_data='bt')
        button_pk = types.InlineKeyboardButton('Parkinsons', callback_data='pk')
        keyboard.add(button_alz, button_bt, button_pk)
        bot.send_message(message.chat.id, "Select", reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, f"Patient {patient_id} does not exist.")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_add = types.InlineKeyboardButton('Create',callback_data='new')
        button_dis = types.InlineKeyboardButton('Exit', callback_data='cancel')
        keyboard.add(button_add, button_dis)
        bot.send_message(message.chat.id, "Do you want to create a new patient or exit?", reply_markup=keyboard)



def create_new_patient(message):
    patient_name = message.text
    with open('patient.txt', 'w') as f:
        f.write(f"{patient_name}")
    patient_id = enter_patient_details_into_database(message,patient_name)
    with open('patient.txt', 'w') as f:
        f.write(f"{patient_id}")
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_add = types.InlineKeyboardButton('Upload',callback_data='existing')
    button_dis = types.InlineKeyboardButton('Cancel', callback_data='cancel')
    keyboard.add(button_add, button_dis)
    bot.send_message(message.chat.id, f"Do you want to upload an MRI scan of {patient_name} or exit?", reply_markup=keyboard)

    

def upload_mri_alzhemeirs(message):
    
    print("in upload mri")
    with open('patient.txt', 'r') as f:
        patient_id = f.read().strip()
    patient_name = supabase.table('patients').select('name').match({'id': patient_id}).execute()
    name = patient_name.data[0]['name']
    bot.send_message(message.chat.id, f"Upload MRI scan of patient {name}.")
    bot.register_message_handler(lambda msg: handle_photo(msg,patient_id), content_types=['photo'])


def handle_photo(message,patient_id):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        with open(local_path, 'wb') as f:
            f.write(downloaded_file)
        val = models.run()
        description = gemini_search.run(val)
        with open('output.txt', 'w') as f:
            f.write(f"{str(val)}\n{patient_id}\n{description}")
        bot.send_message(message.chat.id, f"Result is {val}")
        bot.send_message(message.chat.id, f"Summary:\n{description}")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_add = types.InlineKeyboardButton('Proceed',callback_data='proceed')
        button_dis = types.InlineKeyboardButton('Cancel', callback_data='cancel')
        keyboard.add(button_add, button_dis)
        bot.send_message(message.chat.id, "Click Proceed if to add to the database", reply_markup=keyboard)

    except Exception as e:
        print(f"Error: {e}")
def upload_txt_parkinsons(message):
    bot.send_message(message.chat.id, "Upload the data file")
    bot.register_message_handler(lambda msg: handle_txt(msg), content_types=['document'])

def handle_txt(message):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        with open('uploads/data.txt', 'wb') as f:
            f.write(downloaded_file)
        val = parkinson.value()
        with open('output.txt', 'w') as f:
            f.write(f"{str(val)}\n")
        bot.send_message(message.chat.id, f"Result is {val}")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_add = types.InlineKeyboardButton('Proceed',callback_data='proceed')
        button_dis = types.InlineKeyboardButton('Cancel', callback_data='cancel')
        keyboard.add(button_add, button_dis)
        bot.send_message(message.chat.id, "Click Proceed if to add to the database", reply_markup=keyboard)

    except Exception as e:
        print(f"Error: {e}")
def handle_cancel_callback(callback):
    bot.send_message(callback.message.chat.id, "Task cancelled. Thank you for using the bot.")
# New function to handle the 'proceed' callback
def handle_proceed_callback(callback):
    try:
        print('In proceed')

        with open('output.txt', 'r') as f:
            val = f.readline().strip()
            patient_id = f.readline().strip()
            print(patient_id, "patient_id")
        with open('output.txt', 'r') as file:
            # Skip the first two lines
            for _ in range(2):
                next(file)
            
            
            desc = file.read().strip()
            print(desc)
        val = str(val)
        desc = str(desc)
        patient_id = int(patient_id)
        print(patient_id, val)

        response = supabase.table('scans').select('*').match({'patient_id': patient_id}).execute()
        print(response.data , "response")
        count = len(response.data)
        count += 1
        path = f"{patient_id}/{patient_id}_{count}.jpg"
        with open(local_path, 'rb') as f:
            supabase.storage.from_("Scan_Image").upload(file=f, path=path, file_options={"content-type": "image/jpg, document/txt"})
        print("Added in Scan ", path)
        response_path = supabase.storage.from_('Scan_Image').get_public_url(path)
        # Use supabase.table("scans").upsert(...) instead of .insert
        with open('disease.txt', 'r') as f:
            disease = f.read().strip()
        if disease == "Alzhemeirs":
            supabase.table("scans").insert({"patient_id": patient_id, "output": val, "imageURL": response_path, "description" : desc, "Alzhemeirs": True}).execute()
        elif disease == "Brain Tumor":
            supabase.table("scans").insert({"patient_id": patient_id, "output": val, "imageURL": response_path, "description" : desc, "Tumor" : True}).execute()
        elif disease == "Parkinsons":
            supabase.table("scans").insert({"patient_id": patient_id, "output": val, "imageURL": response_path, "description" : desc, "Parkinsons": True}).execute()
        else:
            print("Error: Unexpected value in 'disease.txt'")
        
        bot.send_message(callback.message.chat.id, f"Added to supabase successfully...")
        
    except Exception as e:
        print(f"Error in handle_proceed_callback: {e}")
        if e.error == "Duplicate":
            count +=1
            path = f"{patient_id}/{patient_id}_{count}.jpg"
            with open(local_path, 'rb') as f:
                supabase.storage.from_("Scan_Image").upload(file=f, path=path, file_options={"content-type": "image/jpg"})
            print("Added in Scan")
            supabase.table("scans").insert({"patient_id": patient_id, "output": val, "imageURL": path}).execute()
            bot.send_message(callback.message.chat.id, f"Added to supabase successfully...")

# Placeholder functions, replace with actual database logic
def check_patient_exists_in_database(patient_id):
    try:
        response = supabase.table('patients').select('*').match({'id': patient_id}).execute()
        print(response.data , "response")
        count = len(response.data)
        if count == 0:
            return False
        else:
            return True
    except Exception as e:
        print(f"Error: {str(e)}")

def enter_patient_details_into_database(message,patient_name):
    try:
        response = supabase.table("patients").insert({"name": patient_name}).execute()

    # The database should automatically assign a unique ID to the new patient
        
        print(response.data, "response")
        patient_id = response.data[0]['id']
        # print(patient_id, "patient_id")
        bot.send_message(message.chat.id, f"Patient {patient_name} created with ID {patient_id}.")
        return patient_id

    except Exception as e:
        print(f"Error: {str(e)}")
    

if __name__ == "__main__":
    # Polling to continuously check for new messages
    bot.polling(none_stop=True)

