import pickle
import json
import time
from difflib import get_close_matches
import boto3
import os
import sys
from tempfile import gettempdir
from contextlib import closing
import subprocess
import pygame


with open('zumzum','rb') as file:
    j = pickle.load(file)
    i= "".join(str(items) for items in j)

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path : str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
        
def find_best_match(user_questions: str, questions: list[str]) -> str or None:
    matches: list = get_close_matches(user_questions, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str or None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

def abot():
    knowledge_base: dict = load_knowledge_base('knowledge.json')
    awscon=boto3.session.Session(profile_name='adi')
    client=awscon.client(service_name='polly',region_name='us-east-1')
    a=1
    while a:
        user_input: str = i
        if user_input.lower() == 'quit':
            break 
        best_match: str | None = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
        if best_match:
            answer: str = get_answer_for_question(best_match, knowledge_base)
            
            response=client.synthesize_speech(Text=answer,Engine='neural',OutputFormat='mp3',VoiceId='Joanna')
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
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
            print(f'BOT: {answer}')
            print(f"Playing audio: {output}")

            try:
                pygame.mixer.music.load(output)  
                pygame.mixer.music.play()  
                while pygame.mixer.music.get_busy():  
                    time.sleep(2)
            except pygame.error as e:
                print(f"Error playing audio: {e}")
                sys.exit(-1)
            
        else:
            print('BOT: tell me')
            new_answer: str = input('Type the answer or "skip" to skip: ')
            
            if new_answer.lower() != 'skip':
                knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                save_knowledge_base('knowledge.json', knowledge_base)
                print('ty')
        a=0
if __name__ == '__main__':
    abot()

