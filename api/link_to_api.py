import requests
import logging

#fast api endpoint 
API_ENDPOINTS = 'http://192.168.31.104:8000/data/'

#function to send the data to the api
def send_data_to_fast_api(buffer):
    for line in buffer:
        try:
            #search for this function 
            sr_no, x, y, z = map(lambda x: x.split(':')[1], line.split(','))
            data = {
                "sr_no": int(sr_no),
                "X": float(x),
                "Y": float(y),
                "Z": float(z)
            }
            response =  requests.post(API_ENDPOINTS, json =data)
            if response.status_code == 200:
                print(f"data sent to api : {data}")
            else:
                print(f"Failed to send the data: {data}")
        except Exception as e:
            logging.error(f"Failed to send data: {e}")

