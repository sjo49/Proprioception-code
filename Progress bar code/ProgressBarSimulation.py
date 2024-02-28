import PySimpleGUI as sg
import time
import numpy as np
from tkinter.filedialog import askdirectory  # Import askdirectory from tkinter
import os

# Define the source folder where you want to save the renamed files
src_folder = askdirectory(title="Select folder to save data to")
# Set the destination folder to be the same as the source folder
dest_folder = src_folder

participant = sg.popup_get_text('Please enter participant number', title="Textbox")
print ("Participant: ", participant)


# set progress bars to be at 10%, 20% and 30% for rounds 1-3
round_values = [(26, 54, 78), (10, 20, 30)]

round_number = sg.popup_get_text('Enter the round', title="Textbox")
print ("You selected round: ", round_number)
set_round = int(round_number)
max_val = 100

# create dictionary to store emg_values array by round number
emg_dict = {}

if set_round > 4:
    text = sg.popup_get_text('Invalid round selected, please enter a round between 1-4', title="Textbox")
    print ("You entered: ", text)
    set_round = int(text)
    if set_round > 4:
        print("Invalid round selected again, please close and start again")
        sg.popup('Invalid round selected again, please close and start again', title='Invalid round')   

while set_round < 4:
    layout = [
        [sg.Text('Progress Bar Simulation')],
        # Simulate a target line at 25% by using a combination of colored text elements
        [sg.Text('|', text_color='red', font=('Helvetica', 18), pad=((round_values[0][set_round-1],0),0)),  # Position marker at roughly 25%
        sg.Text(f'{round_values[1][set_round-1]}%', text_color='red')],
        [sg.ProgressBar(max_val, orientation='h', size=(20, 20), key='progressbar')],
        [sg.Text('|', text_color='red', font=('Helvetica', 18), pad=((round_values[0][set_round-1],0),0)),  # Position marker at roughly 25%
        sg.Text(f'{round_values[1][set_round-1]}%', text_color='red')],
        [sg.Cancel()]
    ]

    # Create the window
    window = sg.Window('Window Title', layout)
    progress_bar = window['progressbar']
    emg_values = []

    # Loop for updating the progress bar
    for i in range(20):
        # Check for window close or cancel button
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        # Update the progress bar
        x = np.random.randint(15,25)
        progress_bar.UpdateBar(x)
        emg_values.append(x)
        time.sleep(0.1)  # Simulate some work being done
    window.close()
    emg_dict[set_round] = emg_values
    print(emg_dict)
    print(f"Round {set_round} completed")

    # Display a yes/no question pop-up to ask if the user is ready to move onto the next round
    ready = sg.popup_yes_no('Are you ready to move onto the next round?', title="Ready for next round?")

    # Check and respond to the user's answer
    if ready == 'Yes':
        set_round += 1
        sg.popup(f'Moving onto round {set_round}', title='Ready response')
        print(f'Moving onto round {set_round}')
    elif ready == 'No':
        exit_question = sg.popup_yes_no('Would you like to exit?', title='Exit or continue')
        if exit_question == 'Yes':
            break
        elif exit_question == 'No':
            sg.popup('Please choose the round to continue', title='Continue')
            text = sg.popup_get_text('Enter the round', title="Textbox")
            print ("You entered: ", text)
            set_round = int(text)
            if set_round > 4:
                text = sg.popup_get_text('Invalid round selected, please enter a round between 1-4', title="Textbox")
                print ("You entered: ", text)
                set_round = int(text)
                if set_round > 4:
                    print("Invalid round selected again, please close and start again")
                    sg.popup('Invalid round selected again, please close and start again', title='Invalid round')
    else:
        sg.popup('No response.', title='Response')
        time.sleep(1)
        break

if set_round == 4:
    layout = [
        [sg.Text('Progress Bar Simulation')],
        [sg.Text('|', text_color='red', font=('Helvetica', 18), pad=((26,0),0)), sg.Text('10%', text_color='red')],       
        [sg.ProgressBar(max_val, orientation='h', size=(20, 20), key='progressbar', bar_color='red on white')],
        [sg.ProgressBar(max_val, orientation='h', size=(20, 20), key='progressbar2')],
        [sg.Text('|', text_color='red', font=('Helvetica', 18), pad=((78,0),0)), sg.Text('30%', text_color='red')],  
        [sg.Cancel()]
    ]

    # Create the window
    window = sg.Window('Window Title', layout)
    progress_bar = window['progressbar']
    progress_bar_2 = window['progressbar2']
    emg_values = []


    # Loop for updating the progress bar
    demo = 10
    for i in range(3):
        # Check for window close or cancel button
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        # make the demonstration progress bar increase from 10 to 30 and back down again slowly 3 times
        # create a value y that increases from 10 to 30 and back down again
        while demo < 30:
            demo += 1
            i += 1 
            progress_bar.UpdateBar(demo)

            # Update the progress bar
            x = np.random.randint(15,25)
            progress_bar_2.UpdateBar(x)
            emg_values.append(x)
            time.sleep(0.1)  # Simulate some work being done
        while demo > 10:
            demo -= 1
            i += 1
            progress_bar.UpdateBar(demo)
            # Update the progress bar
            x = np.random.randint(15,25)
            progress_bar_2.UpdateBar(x)
            emg_values.append(x)
            time.sleep(0.1)
    window.close()
    emg_dict[set_round] = emg_values
    print(emg_dict)
    print(f"Round {set_round} completed")
    

print(emg_dict)

# create file to save the emg_dict to
file = open('emg_dict.txt', 'w')
file.write(str(emg_dict))


# Create the new filename
new_filename = f"Participant_{participant}_EMG_data"
new_file_path = os.path.join(dest_folder, new_filename)  # Make sure 'dest_folder' is defined
np.save(new_file_path, emg_dict)



# else:
#     print("Invalid round selected, please start again")
#     sg.popup('Invalid round selected, please start again', title='Invalid round')
#     # text = sg.popup_get_text('Invalid round selected, please enter a round between 1-4', title="Textbox")
#     # print ("You entered: ", text)
#     # set_round = int(text)


# import os
# size = os.path.getsize('zen.txt')
# file=open("zen.txt")
# i=0
# while True:
#    text=file.read(1)
#    i=i+1
#    if text=="":
#       file.close()
#       break
#    print (text,end='')
#    sg.one_line_progress_meter(
#       'Progress Meter', i, size,
#       'Character Counter')
#    time.sleep(0.2)
   

