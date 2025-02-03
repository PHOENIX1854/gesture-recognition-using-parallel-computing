import tkinter as tk
import boto3
import os
import sys
from tempfile import gettempdir
from contextlib import closing
import subprocess
import mpv

root=tk.Tk()
root.geometry("400x240")
root.title("T2S")

textexample=tk.Text(root,height=10)
textexample.pack()



def gt():
    awscon=boto3.session.Session(profile_name='adi')
    client=awscon.client(service_name='polly',region_name='us-east-1')
    r=textexample.get("1.0","end")
    print(r)
    response=client.synthesize_speech(Text=r,Engine='neural',OutputFormat='mp3',VoiceId='Joanna')
    if "AudioStream" in response:
        with closing(response['AudioStream']) as stream:
            output=os.path.join(gettempdir(),"speech.mp3")
            try:
                with open(output,"wb") as file:
                    file.write(stream.read())
            except IOError as error:
                sys.exit(-1)  
    else:
        print("No stream founded")
        sys.exit(-1)
    player = mpv.MPV()
    player.play(output)
    
btnr=tk.Button(root,height=1,width=10,text="Read",command=gt)
btnr.pack()

root.mainloop()