from configuration.config import COM_PORT, BAUD_RATE
import serial
import threading
import logging
import time
from logger_config import setup_logging , log_file_completion
from api.link_to_api import send_data,send_data_via_Websocket
from datetime import datetime
 

# buffer_size_limit = 200
buffer1 = []
buffer2 = []

active_buffer = 0
lock = threading.Lock() #locking particular thread to stop the interfarence of another thread in between first thread
write_confirm = False



ser = serial.Serial(COM_PORT, BAUD_RATE)
stop_event = threading.Event()

highest_srno = 30000

file_counter = 1

def get_new_txt_filename():
    global file_counter
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d-%H%M%S")  # Format as YYYY-MM-DD_HH-MM-SS
    filename = f"{formatted_time}.txt"
    file_counter += 1
    return filename

def read_data():
    global active_buffer, highest_srno,text_file_name,write_confirm
    try: 
        print(f"Connected to the sensor with the above credentials") 
        while not stop_event.is_set():
            if ser.in_waiting > 0:  # Check if there is data available to read  
                data = ser.readline().decode('utf-8', errors = 'replace')
                try:                   
                    SerialNo, x, y, z = map(int, data.split(','))
                    print(f"SRNO:{SerialNo}, X:{x}, Y:{y}, Z:{z},Buffer status: {active_buffer}")
                    
                    if active_buffer == 0:
                        buffer1.append(f"SRNO:{SerialNo},X:{x},Y:{y},Z:{z}")
                    else:
                        buffer2.append(f"SRNO:{SerialNo},X:{x},Y:{y},Z:{z}")

                     # Send data to API immediately
                    send_data([f"SRNO:{SerialNo},X:{x},Y:{y},Z:{z}"])
                    send_data_via_Websocket([f"SRNO:{SerialNo},X:{x},Y:{y},Z:{z}"])

                    with lock:
                        # response_active_buffer = SerialNo % highest_srno
                        response_active_buffer = SerialNo % highest_srno
                        if response_active_buffer == 0:  
                            if SerialNo >= highest_srno:    
                                text_file_name = get_new_txt_filename()
                                switch_buffers()
                                write_confirm  = True       
                except ValueError:
                    print(f"Error: Data format incorrect, skipping this line")

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        if ser.is_open:
             ser.close()
             print("Serial connection closed.")

def switch_buffers():
    global active_buffer, buffer1 , buffer2
    if active_buffer == 0:
        active_buffer = 1
    else:
        active_buffer = 0

def write_data_to_file():
    global text_file_name,buffer1,buffer2,write_confirm

    while not stop_event.is_set():
        time.sleep(1)
        if write_confirm == True:
            with lock:
                try: 
                    if active_buffer == 1:
                        with open(text_file_name, 'a') as f:#it wil write the file
                            for line in buffer1:
                                f.write(line + '\n')
                        f.close()
                        # send_data_to_fast_api(buffer1)
                        buffer1.clear()
                    else:
                        with open(text_file_name, 'a') as f:#it wil write the file
                            for line in buffer2:
                                f.write(line + '\n')
                        f.close()
                        # send_data_to_fast_api(buffer2)
                        buffer2.clear()   

                    log_file_completion(text_file_name, "completed")  
                    write_confirm = False
                except IOError as e:
                    logging.error(f"File error: {e}")
                    log_file_completion(text_file_name, f"failed: {e}")

if __name__ == "__main__":
   
    setup_logging

    # logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    read_thread = threading.Thread(target= read_data)
    write_thread = threading.Thread(target=write_data_to_file)

    write_thread.daemon = True
    write_thread.start()
    read_thread.start()
    
    try:
        read_thread.join()
        read_thread.join()
        write_thread.join()
    except KeyboardInterrupt:
        print("Stopping...")
        stop_event.set()
        print("Program terminated.")
