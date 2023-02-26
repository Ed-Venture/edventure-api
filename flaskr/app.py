from flask import Flask,request,jsonify,current_app,send_file
import logging
from firebase_admin import credentials, firestore, initialize_app
from dotmap import DotMap
import os
import urllib.request
from PyPDF2 import PdfMerger

app = Flask(__name__)
# Initialize Firestore DB
# filename = os.path.join('firebase', os.path.basename('key.json'))
# urllib.request.urlretrieve("https://firebasestorage.googleapis.com/v0/b/ed-tech-ureckathon.appspot.com/o/keys%2Fkey.json?alt=media&token=895a4d73-dfef-4315-9b2d-f80de976ca5f", filename) 
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
assign_ref = db.collection('assignments')
folder_path = 'files'

@app.route("/assign",methods=["POST"])
def fetch_file():
    # id = request.json['id']
    # return f'Ass {db}'
    try:
        if len(os.listdir(folder_path)) > 0:
    # Loop through all the files in the folder and delete them
           for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f'Deleted {file_path}')
                except Exception as e:
                    print(f'Error deleting {file_path}: {e}')
        # print("Hello",flush=True)
        # Check if ID was passed to URL query
        assign_id = request.json['id']
        print(assign_id,flush=True)
        if assign_id:
            assign = assign_ref.document(assign_id).get()
            a=DotMap(assign.to_dict())
            print(a.files_url)
            files=a.files_url
            folder='files'
            for count,fi in enumerate(files):
                print(fi,count)
                if not os.path.exists(folder):
                   os.makedirs(folder)
                filename = os.path.join(folder, os.path.basename(f'{count}.pdf'))
                urllib.request.urlretrieve(fi, filename)  
            pdf_merger = PdfMerger()
            for filename in os.listdir(folder_path):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(folder_path, filename)
                    pdf_merger.append(file_path)
            output_path = os.path.join(folder_path, 'merged.pdf')
            with open(output_path, 'wb') as output_file:
                pdf_merger.write(output_file)
            file_path = os.path.join(os.path.dirname(__file__), 'FILES', 'merged.pdf')
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                 return jsonify(assign.to_dict()), 200                 
           
        else:
            all_assigns = [doc.to_dict() for doc in assign_ref.stream()]
            return jsonify(all_assigns), 200
    except Exception as e:
        return f"An Error Occurred: {e}"