import serial

import customtkinter
from customtkinter import filedialog

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("600x600")
root.resizable()


def validation(address, filename, port):
    counter = 1
    # Clear the text box
    outputFrame.delete("1.0", "end")
    # Read the data from the file we want to validate and split it into 8 byte chunks
    data = read_file(filename)
    chunks = [data[i:i + 8] for i in range(0, len(data), 8)]
    # Generate dummy data to send through the ftdi in order to receive the data from memory

    try:
        for chunk in chunks:
            dummy_data = generate_dummy_data(address)
            # Send dummy data and receive data from memory
            send_data(dummy_data, port)
            received_data = receive_data(port, 8)

            # verify if data in file is the same as the data from memory
            if received_data == chunk:
                outputFrame.insert(str(counter) + ".0", text=str(chunk) + "=" + str(received_data) + "OK \n")
                outputFrame.see("end")
                root.update_idletasks()
            else:
                outputFrame.insert(str(counter) + ".0", text=str(chunk) + "=" + str(received_data) + "NOT OK \n")
                outputFrame.see("end")
                root.update_idletasks()
            address = address + 1
            counter += 1
    except serial.SerialException as e:
        print("There was an error trying to send the file", e)

    finally:
        print("test successful")


def generate_dummy_data(address):
    address_bytearray = bytearray(8)
    command_bytearray = bytearray(1)
    for i in range(8):
        address_bytearray[-(i + 1)] = address >> (8 * i) & 0xFF

    command_bytearray[-(0 + 1)] = 2 >> 0 & 0xFF
    dummy_data = [0, 0, 0, 0, 0, 0, 0, 0]
    dummy_data_bytes = bytearray(dummy_data)
    # Concatenate the bytearrays
    concatenated_chunk = command_bytearray + address_bytearray + dummy_data_bytes
    return concatenated_chunk


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


def format_received_data(data):
    # Split the data into chunks
    chunks = [data[i:i + 8] for i in range(0, len(data), 8)]
    # Concatenate additional bits to each chunk
    formatted_chunks = []
    for chunk in chunks:
        # Convert chunk to bytearray
        chunk_bytearray = bytearray(chunk)
        # Append to the list
        formatted_chunks.append(chunk_bytearray)

    # Return the list of bytearrays
    return formatted_chunks


def format_data(data, address, command):
    # Split the data into chunks
    chunks = [data[i:i + 8] for i in range(0, len(data), 8)]
    # Add an End Of File
    chunks.append(bytearray("EndOFile", "utf-8"))
    # Concatenate additional bits to each chunk
    formatted_chunks = []
    for chunk in chunks:
        # Convert chunk to bytearray
        chunk_bytearray = bytearray(chunk)

        # Convert address and command to bytearray
        address_bytearray = bytearray(8)
        command_bytearray = bytearray(1)

        for i in range(8):
            address_bytearray[-(i + 1)] = address >> (8 * i) & 0xFF

        command_bytearray[-(0 + 1)] = command >> 0 & 0xFF

        # Concatenate the bytearrays
        concatenated_chunk = command_bytearray + address_bytearray + chunk_bytearray

        # Append to the list
        formatted_chunks.append(concatenated_chunk)
        address = address + 1

    # Concatenate an EOF at the last+1 memory address

    # Return the list of bytearrays
    return formatted_chunks


def send_file():
    outputFrame.delete("1.0", "end")
    counter = 1
    sendButton.configure(state="disabled")
    file_name = label3.cget("text")
    port = portVar.get()
    # print(port)

    address = int(addressEntry.get(), 16)
    command = int(commandEntry.get())
    port1 = serial.Serial(port, 115200, timeout=1)
    if command == 1:
        data = read_file(file_name)
        if file_name == "":
            sendButton.configure(state="enabled")
            return
        formatted_data = format_data(data, address, command)
        try:
            #
            testfile = open('test.hex', 'wb')
            for data_package in formatted_data:
                testfile.write(data_package)
                send_data(data_package, port1)
                print(data_package)

                # Print data in Label

                outputFrame.insert(str(counter) + ".0", text=str(data_package) + '\n')
                outputFrame.see("end")
                root.update_idletasks()
                counter += 1
            # Finish print

            # Only for tests
            # received_data = receive_data(port1, len(data))
            # print(received_data)
            # save_file("test.hex", received_data)#

        except serial.SerialException as e:
            print("There was an error trying to send the file", e)

        finally:
            # print("test successful")
            outputFrame.configure(state="disabled")
            sendButton.configure(state="normal")
            port1.close()

    elif command == 2:
        try:
            # Open the file to store the data read from memory
            fileread = open("file_read.hex", 'wb')

            # Start a counter for changing lines in the textbox
            counter = 1
            # Create an End of File byte array to compare with the received data
            endOfFile = bytearray("EndOFile", 'utf-8')
            address_aux = address
            while True:
                # Generate the dummy data to send through the FTDI in order to receive the data from memory
                dummy_data = generate_dummy_data(address_aux)
                # Send the dummy data and then receive the data read from memory
                send_data(dummy_data, port1)
                received_data = receive_data(port1, 8)

                # If there's no data break the loop and return
                if not received_data:
                    outputFrame.insert(str(counter) + ".0", "No Data Found")
                    outputFrame.see("end")
                    counter += 1
                    root.update_idletasks()
                    break
                # When the end of file is detected we break the loop and return
                if received_data == endOfFile:
                    root.update_idletasks()
                    break
                # Print the received data into the textbox
                outputFrame.insert(str(counter) + ".0", text=str(received_data) + '\n')
                outputFrame.see("end")
                root.update_idletasks()
                # Write the received data into the file
                fileread.write(received_data)
                address_aux = address_aux + 1
            validation(address, "file_read.hex", port1)

        except serial.SerialException as e:
            print("There was an error trying to send the file", e)

        finally:
            print("test successful")
            sendButton.configure(state="normal")
            port1.close()

    else:
        print("Command Unknown")
        sendButton.configure(state="normal")


def find_ports():
    ports = ['COM%s' % (i + 1) for i in range(256)]
    found = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            found.append(port)
        except (OSError, serial.SerialException):
            pass
    return found


def browse_file():
    filepath = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("All files", "*.*"),))
    label3.configure(text=filepath)


if __name__ == '__main__':
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

    addressEntry = customtkinter.CTkEntry(master=frame, placeholder_text="ADDRESS")
    addressEntry.pack(pady=12, padx=10)

    commandEntry = customtkinter.CTkEntry(master=frame, placeholder_text="COMMAND")
    commandEntry.pack(pady=12, padx=10)

    portVar = customtkinter.StringVar()
    portValues = find_ports()
    portComboBox = customtkinter.CTkComboBox(master=frame, values=portValues, variable=portVar)
    portComboBox.pack(pady=12, padx=10)

    sendButton = customtkinter.CTkButton(master=frame, text="SEND", command=send_file)
    sendButton.pack(pady=12, padx=10)

    outputFrame = customtkinter.CTkTextbox(master=frame, width=400, height=300)
    outputFrame.pack(pady=12, padx=10)
    # Output to read

    root.mainloop()
