import speech_recognition as sr
import os
import moviepy.editor as mp
from pydub import AudioSegment

#load mp4 ad extract wav track
print('Loading video...')
files = os.listdir()
video_name = False
for f in files:
    if f.endswith('.mp4'):
        video_name = f
        break

video = mp.VideoFileClip(video_name)
audio_file_name = 'track.wav'
print('Extracting audio...')
video.audio.write_audiofile(audio_file_name)


#split audio file
print('Splitting audio...')
command = 'sh ST.sh '+ audio_file_name +' -30 1'
os.system(command)
silences = open('silence.txt', 'r').readlines()
audio_file = AudioSegment.from_mp3(audio_file_name)
last = 0
tracks = []
for line in silences:
    end,duration = line.strip().split()
    try:
        to = (float(end) - float(duration)) * 1000
        start = float(last) * 1000
        clip_len = to - start
        #if clip last less than 5 sec it doesn't split
        if clip_len > 5000:
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
    f = 'temp.wav'
    track.export(f, format='wav')
    with sr.AudioFile(f) as source:
        audio = r.record(source)
        try:
            r_text = r.recognize_google(audio, language="it-IT")
        except:
            r_text = 'ERROR'
        text +='\n' + r_text
        name = video_name.replace('.mp4', '.txt')
        text_file = open(name, 'w+')
        text_file.writelines(text)
        text_file.close()
        print(r_text)
