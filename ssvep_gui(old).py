import tkinter as tk
import pylsl
import time as t

max_duration = 3           # flash duration (s)
interval = 1000
mrkstream = None           # Global variable for LSL marker stream (Initialized in main)
colors = ['white', 'red']
button_flashing = False
timing = False
route = []

def flashColor(object, colorind, delay):
    global button_flashing

    if button_flashing:
        object.config(bg = colors[colorind])
        root.after(delay, flashColor, object, 1 - colorind, delay)
    else:
        object.config(bg = colors[1])

root = tk.Tk()
root.geometry('1500x700')

left_f = tk.Frame(root, width=200, height=200, bg='red')
left_f.place(relx=0, rely=0, anchor='nw')#x=0, y=225

right_f = tk.Frame(root, width=200, height=200, bg='red')
right_f.place(relx=1, rely=1, anchor='se')#x=1250, y=225

top_f = tk.Frame(root, width=200, height=200, bg='red')
top_f.place(relx=1, rely=0, anchor='ne')#x=625

bot_f = tk.Frame(root, width=200, height=200, bg='red')
bot_f.place(relx=0, rely=1, anchor='sw')#x=625, y=450

def flash():
    flashColor(left_f, 0, 83)    # ~6Hz
    flashColor(top_f, 0, 56)     # ~9Hz
    flashColor(bot_f, 0, 42)     # ~12Hz
    flashColor(right_f, 0, 33)   # ~15Hz

def timer(duration, interval):
    global button_flashing
    global timing
    global max_duration

    if timing:
        #print(t.time(), duration, button_flashing)
        duration -= 1

        if duration <= -1:
            button_flashing = not button_flashing
            duration = max_duration
            #mrkstream.push_sample(pylsl.vectorstr(['0']))

        elif duration == max_duration-1:
            button_flashing = not button_flashing
            flash()
            #mrkstream.push_sample(pylsl.vectorstr(['1']))

        root.after(interval, timer, duration, interval)
    else:
        button_flashing = False

def buttonCallback(self):
    global button_flashing
    global timing

    timing = not timing
    if timing:
        self.config(text = 'Press to stop flashing')
        timer(max_duration, interval)
    else:
        self.config(text = 'Press to start flashing')

my_button = tk.Button(root, text = 'Press to start flashing',
                      command = lambda:buttonCallback(my_button))
my_button.place(relx=0.5, rely=0, anchor='n')


def CreateMrkStream():
    info = pylsl.stream_info('SSVEP_Markers', 'Markers', 1, 0, pylsl.cf_string, 'unsampledStream');
    outlet = pylsl.stream_outlet(info, 1, 1)
    return outlet;

if __name__ == "__main__":

    # Initialize LSL marker stream
    #mrkstream = CreateMrkStream();
    t.sleep(0.5)

    # Init app
    root.mainloop()
