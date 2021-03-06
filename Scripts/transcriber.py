import os
import config

#Define transciption language
LANGUAGE = config.language
SILECE_THRESHOLD = '-30' #value in dB, noises lower than silence_threshold are considered as silence

#install missing libraries
try:
    import moviepy.editor as mp
except:
    try:
        os.system('pip3 install moviepy')
        import moviepy.editor as mp
    except:
        os.system('pip install moviepy')
        import moviepy.editor as mp

try:
    from pydub import AudioSegment
except:
    try:
        os.system('pip3 install pydub')
        from pydub import AudioSegment
    except:
        os.system('pip install pydub')
        from pydub import AudioSegment

try:
    import speech_recognition as sr
except:
    try:
        os.system('pip3 install SpeechRecognition')
        import speech_recognition as sr
    except:
        os.system('pip install SpeechRecognition')
        import speech_recognition as sr


def extract_audio(video_name, audio_file_name):
    video = mp.VideoFileClip(video_name)
    print('Extracting audio...')
    video.audio.write_audiofile(audio_file_name)


def split_audio(audio_file_name):
    #split audio file
    print('Splitting audio...')

    #Create silence.txt file where are contained all the start and end seconds of all the silences
    #-30 is the dB silence threshold, 1 is the minimum silence duration
    command = 'sh Scripts/ST.sh '+ audio_file_name + ' '+ SILECE_THRESHOLD +' 1' 
    os.system(command)

    #read all the silences times
    silences = open('silence.txt', 'r').readlines()
    audio_file = AudioSegment.from_mp3(audio_file_name)
    last = 0
    tracks = []

    #extract all audio segments from audio source splitting where a silince was previously detected
    for line in silences:
        end,duration = line.strip().split()
        try:
            #calculate audio start and end
            #library works in ms so it's all multiplied by 1000 to get seconds
            to = (float(end) - float(duration)) * 1000
            start = float(last) * 1000
            clip_len = to - start
            #if clip last less than 5 sec it doesn't split
            if clip_len > 5 * 1000:
                #extract an audio segment from the source and add 0.5 s of silence at start and at the end of the segment for better transcription 
                audio_segment = AudioSegment.silent(500) + audio_file[start:to] + AudioSegment.silent(500)
                tracks.append(audio_segment)
                last = end
        except:
            pass
    print('Done')
    return tracks



def transcribe_tracks(tracks, text_file_name):
    #initialize the recogniser
    r = sr.Recognizer()
    text = ''

    #transcribe all audio segments
    for track in tracks:
        #Create a temp file from the audio segment
        f = 'temp.wav'
        track.export(f, format='wav')
        with sr.AudioFile(f) as source:
            audio = r.record(source)
            #Gets transcription of the audio segment
            try:
                #try to transcribe from google server
                r_text = r.recognize_google(audio, language=LANGUAGE)
                #Append a new transcribed line of text to the transcription
                text +='\n' + r_text
                text_file = open(text_file_name, 'w+')
                text_file.writelines(text)
                text_file.close()
                print(r_text)
            except:
                #notify error
                print('ERROR')



def transcribe(video_name, video_folder = ''):
    audio_file_name = 'track.wav'
    #load mp4 ad extract wav track
    print('Loading video...')
    # create audio file id doesn't exists
    #if not os.path.isfile(audio_file_name):
    #    open(audio_file_name, 'w')
    extract_audio(video_folder + video_name, audio_file_name)
    #transcript audio
    print('Starting transcription...')
    text_file_name = video_name.replace('.mp4', '.txt') #set .txt file name to video source name
    print('Writing text to {}'.format(text_file_name))
    tracks = split_audio(audio_file_name)
    transcribe_tracks(tracks,text_file_name)
    #end transcription
    print('\ntranscpription terminated')
    return(text_file_name)
