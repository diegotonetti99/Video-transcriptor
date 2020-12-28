import speech_recognition as sr
import os
import moviepy.editor as mp
from pydub import AudioSegment


#Define transciption language
LANGUAGE = 'it-IT'
SILECE_THRESHOLD = '-30' #value in dB, lower noises are considered as silence

#load mp4 ad extract wav track
print('Loading video...')
files = os.listdir()
video_name = False
for f in files:
    if f.endswith('.mp4'):
        video_name = f
        break

if not video_name:
    print('No video found')
    exit()
else:
    print('{} found'.format(video_name))
video = mp.VideoFileClip(video_name)
audio_file_name = 'track.wav'
print('Extracting audio...')
video.audio.write_audiofile(audio_file_name)


#split audio file
print('Splitting audio...')
#Create silence.txt file where are contained all the start and end seconds of all the silences
command = 'sh ST.sh '+ audio_file_name + ' '+ SILECE_THRESHOLD +' 1' #-30 is the dB silence threshold, 1 is the minimum silence duration
os.system(command)
silences = open('silence.txt', 'r').readlines()
audio_file = AudioSegment.from_mp3(audio_file_name)
last = 0
tracks = []
for line in silences:
    end,duration = line.strip().split()
    try:
        #library works in ms so it's all multiplied by 1000
        to = (float(end) - float(duration)) * 1000
        start = float(last) * 1000
        clip_len = to - start
        #if clip last less than 5 sec it doesn't split
        if clip_len > 5 * 1000:
            #extract an audio segment from the source
            tracks.append(audio_file[start:to])
            last = end
    except:
        pass
print('Done')



#transcript audio
print('Starting transcription...')
text = ''
r = sr.Recognizer()
for track in tracks:
    #Create a temp file from the audio segment
    f = 'temp.wav'
    track.export(f, format='wav')
    with sr.AudioFile(f) as source:
        audio = r.record(source)
        #Gets transcription of the audio segment
        try:
            r_text = r.recognize_google(audio, language=LANGUAGE)
        except:
            r_text = 'ERROR'
        #Append a new transcribed line of text to the transcription
        text +='\n' + r_text
        name = video_name.replace('.mp4', '.txt')
        text_file = open(name, 'w+')
        text_file.writelines(text)
        text_file.close()
        print(r_text)
