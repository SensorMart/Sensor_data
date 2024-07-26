import requests
import logging
import asyncio
import json
import websockets
#fast api endpoint 
API_ENDPOINTS = 'http://192.168.31.104:8000/data/'
WEBSOCKET_ENDPOINTS ='ws://192.168.31.104:8000/ws'


def send_data(data):
    for line in data:
        try:
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
                print(f"Failed to send the data: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to send data: {e}")


async def send_data_via_Websocket(data):
    try: 
        async with websockets.connect(WEBSOCKET_ENDPOINTS) as websocket:
            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            # if response == True:
            print(f"response from ws: {response}")
            # else:
            #     print(f"not connected to web socket: {response.status}")
    except Exception as e:
        print(f"error: {e}")

#function to send the data to the api
# async def send_data_to_fast_api(data):
#     send_data(data)
    # await send_data_via_websocket(data)

