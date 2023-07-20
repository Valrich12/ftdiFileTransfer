import serial

import customtkinter
from customtkinter import filedialog

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("600x600")


def send_data(data, port):
    port.write(data)
    return


def receive_data(port, size):
    data = port.read(size)
    return data


def read_file(file_name):
    with open(file_name, "rb") as file:
        data = file.read()
    return data


def save_file(file_name, data):
    with open(file_name, "wb") as archivo:
        archivo.write(data)


def send_file():
    file_name = label3.cget("text")
    data = read_file(file_name)
    port1 = serial.Serial("COM4", 115200, timeout=1)
    try:
        #
        send_data(data, port1)

        # Only for tests
        # received_data = receive_data(port1, len(data))
        # save_file("prueba.rar", received_data)

    except serial.SerialException as e:
        print("There was an error trying to send the file", e)

    finally:
        #
        port1.close()


def browse_file():
    filepath = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("All files", "*.*"),))
    label3.configure(text=filepath)


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="ftdi File Transfer", font=("Roboto", 24))
label.pack(pady=12, padx=10)

label2 = customtkinter.CTkLabel(master=frame, text="File Path", font=("Roboto", 24))
label2.pack(pady=12, padx=10)

label3 = customtkinter.CTkLabel(master=frame, text="", font=("Roboto", 16))
label3.pack(pady=12, padx=10)

chooseFileButton = customtkinter.CTkButton(master=frame, text="CHOOSE FILE", command=browse_file)
chooseFileButton.pack(pady=12, padx=10)

sendButton = customtkinter.CTkButton(master=frame, text="SEND", command=send_file)
sendButton.pack(pady=12, padx=10)

root.mainloop()
