import time
import EMGsqPlusClass as EMGdev
import EMGfiltersCONFIDENTIAL as EMGfilt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calibrate_function import calibrate
import PySimpleGUI as sg
import keyboard
from tkinter.filedialog import askdirectory  # Import askdirectory from tkinter
import os



def close_window(window):
    window.destroy()

def draw_emg(X,Y,position):
    plt.figure(figsize=(5,2))
    plt.plot(X,Y, 'r-')
    plt.ylabel(f"Channel {position}")
    return plt.gcf()

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()

def draw_fig_canvas(canvas, fig): 
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side = 'top', fill = 'both', expand = 1)
    return figure_canvas_agg

# Define the source folder where you want to save the renamed files
src_folder = askdirectory(title="Select folder to save data to")
# Set the destination folder to be the same as the source folder
dest_folder = src_folder

participant = sg.popup_get_text('Please enter participant number', title="Textbox")
print ("Participant: ", participant)

calibration_yes_no = sg.popup_yes_no('Do you need to calibrate?', title="Calibration")
if calibration_yes_no == 'Yes':
    calibration = True
elif calibration_yes_no == 'No':
    calibration = False

#Setting up EMG and Filtering parameters
# calibration = True
emgMode = 1
chanNumb = 8
windowSize = 200 #in datapoints
fs = 2000 #sampling frequency
lowcut = 20 
highcut = 500
envelopecut = 2
emg_data=np.zeros((windowSize,chanNumb+4))
emg_filters = EMGfilt.EMGfilters(lowcut,highcut,envelopecut,fs,ch_numb=chanNumb)
emg=EMGdev.Sessantaquattro(mode=emgMode,nch=0, )
emg.connect_to_sq()


if calibration:
    max_cal_1, max_cal_2, min_cal_1, min_cal_2 = calibrate(emg)
    # create a file to store the calibration values
    calibration_filename = f"calibration_vals"
    new_file_path_calibration = os.path.join(dest_folder, calibration_filename)  # Make sure 'dest_folder' is defined
    np.save(calibration_filename, [max_cal_1, max_cal_2, min_cal_1, min_cal_2])
else:
    try:
        max_cal_1, max_cal_2, min_cal_1, min_cal_2 = np.load('calibration_vals/values.npy')

    except:
        print('Error no file available found')


#Connect to EMG

#loops for x seconds throughout which EMG data is read, converted to float, and filtered
loopTime = 20
time_unit = 0
time_limit = (loopTime*(fs/windowSize))
nyq = fs/2
# max_val =  40
# max_val_2 =  33
# min_val =  4
# min_val_2 =  3
max_val =  max_cal_1
max_val_2 =  max_cal_2
min_val =  min_cal_1
min_val_2 =  min_cal_2


print( max_cal_1, max_cal_2, min_cal_1, min_cal_2)

# set progress bars to be at 10%, 20% and 30% for rounds 1-3
round_values = [(26, 54, 78), (10, 20, 30)]

round_number = sg.popup_get_text('Enter the round', title="Textbox")
print ("You selected round: ", round_number)
set_round = int(round_number)

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
    # Define the layout of the window   
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

    i = 0

    # if set_round <4:

    # Create the window
    window = sg.Window('Window Title', layout)
    progress_bar = window['progressbar']
    emg_values = []

    for i in range(100):
        #EMG data collection and filtering
        emg_data,bin_data=emg.read_emg()
        emg_float = emg_data[:,0:8].astype(float)

        emg_hp=emg_filters.butter_highpass_filter(emg_float)
        emg_lp=emg_filters.butter_lowpass_filter(emg_hp)
        emg_bs=emg_filters.butter_bandstop_filter(emg_lp)
        emg_abs = np.abs(emg_bs)
        emg_env=emg_filters.butter_lowpassEnv_filter(emg_abs)

        emg_filt_1 = emg_env[:,0]
        emg_val = np.mean(emg_filt_1)
        emg_filt_2 = emg_env[:,1]
        emg_val_2 = np.mean(emg_filt_2)

        if emg_val > max_val:
                emg_val = max_val
        
        if emg_val_2 > max_val_2:
                emg_val_2 = max_val_2

        # # create a progress bar from PySimpleGUI and update it with the value of emg_val
        # layout = [[sg.ProgressBar(max_val, orientation='h', size=(20, 20), key='progbar')]]
        # window = sg.Window('Progress Bar Example', layout, finalize=True)
        # window['progbar'].update_bar(emg_val)
        # event, values = window.read(timeout=0)

        # Check for window close or cancel button
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        # Update the progress bar
        progress_bar.UpdateBar(emg_val-min_val)
        emg_values.append(emg_val-min_val)
        i += 1
        if keyboard.is_pressed('q'):
            print("END")
            break
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
            progress_bar.UpdateBar(demo)

            # Update the progress bar
            emg_data,bin_data=emg.read_emg()
            emg_float = emg_data[:,0:8].astype(float)

            emg_hp=emg_filters.butter_highpass_filter(emg_float)
            emg_lp=emg_filters.butter_lowpass_filter(emg_hp)
            emg_bs=emg_filters.butter_bandstop_filter(emg_lp)
            emg_abs = np.abs(emg_bs)
            emg_env=emg_filters.butter_lowpassEnv_filter(emg_abs)

            emg_filt_1 = emg_env[:,0]
            emg_val = np.mean(emg_filt_1)
            emg_filt_2 = emg_env[:,1]
            emg_val_2 = np.mean(emg_filt_2)

            if emg_val > max_val:
                    emg_val = max_val

            progress_bar_2.UpdateBar(emg_val-min_val)
            emg_values.append(emg_val-min_val)
            i += 1 
            if keyboard.is_pressed('q'):
                print("END")
                break

        while demo > 10:
            demo -= 1
            i += 1
            progress_bar.UpdateBar(demo)
            # Update the progress bar
            x = np.random.randint(15,25)
            progress_bar_2.UpdateBar(x)
            emg_values.append(x)
            if keyboard.is_pressed('q'):
                print("END")
                break
    window.close()
    emg_dict[set_round] = emg_values
    print(emg_dict)
    print(f"Round {set_round} completed")



else:
    print("Invalid round selected, please restart")

print(emg_dict)


# Create the new filename
new_filename = f"Participant_{participant}_EMG_data"
new_file_path = os.path.join(dest_folder, new_filename)  # Make sure 'dest_folder' is defined
np.save(new_file_path, emg_dict)



#Disconnect the EMG device after the for-loop has finished    
emg.disconnect_from_sq()
