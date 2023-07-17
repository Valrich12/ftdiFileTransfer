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


def archivo_a_bytes(nombre_archivo):
    with open(nombre_archivo, "rb") as archivo:
        contenido = archivo.read()
    return contenido


def guardar_archivo(nombre_archivo, contenido):
    with open(nombre_archivo, "wb") as archivo:
        archivo.write(contenido)


def send_file():
    file_name = label3.cget("text")
    port1 = serial.Serial("COM4", 115200, timeout=1)
    try:
        # Envia el archivo desde el primer dispositivo al segundo dispositivo
        data = archivo_a_bytes(file_name)
        send_data(data, port1)
        print("Estado de envío: Enviando")

        # Recibe la cadena en el segundo dispositivo desde el primer dispositivo
        received_data = receive_data(port1, len(data))
        guardar_archivo("prueba.rar", received_data)
        print("Cadena recibida:", received_data)

    except serial.SerialException as e:
        print("Ocurrió un error al abrir el puerto serie:", e)

    finally:
        # Cierra las conexiones seriales
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
