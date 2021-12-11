import os
import config

from threading import Thread

# Define transciption language
LANGUAGE = config.language
# value in dB, noises lower than silence_threshold are considered as silence
SILECE_THRESHOLD = config.silence_threshold


# install missing libraries
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
    from pydub import AudioSegment, silence
except:
    try:
        os.system('pip3 install pydub')
        from pydub import AudioSegment, silence
    except:
        os.system('pip install pydub')
        from pydub import AudioSegment, silence

try:
    import speech_recognition as sr
except:
    try:
        os.system('pip3 install SpeechRecognition')
        import speech_recognition as sr
    except:
        os.system('pip install SpeechRecognition')
        import speech_recognition as sr



class Transcriber(Thread):
    def __init__(self, video_source, text_viewer, callback):
        super(Transcriber, self).__init__()

        self.daemon = True
        self.video_name = video_source
        self.text_viewer = text_viewer
        self.text_file_name = ''
        self.loop = True
        self.callback = callback
        self.isEnded=False

    def run(self):
        self.transcribe()
        self.isEnded=True
        self.callback(self)


    def split_audio(self):
        # split audio file
        print('Splitting audio...')
        #silence_file = (self.audio_file_name.replace(
        #    '.wav', '_silence.txt')).replace(' ','').strip()
        # Create silence.txt file where are contained all the start and end seconds of all the silences
        # -30 is the dB silence threshold, 1 is the minimum silence duration
        #command = 'sh Scripts/ST.sh ' + self.audio_file_name + \
        #    ' ' + str(SILECE_THRESHOLD) + ' 1 ' + silence_file
        #os.system(command)
        
        # read all the silences times
        # silences = open(silence_file, 'r').readlines()
        audio=AudioSegment.from_file(self.audio_file_name)
        silences=silence.detect_silence(audio, min_silence_len=1000, silence_thresh=SILECE_THRESHOLD)

        audio_file = AudioSegment.from_mp3(self.audio_file_name)
        last=0
        tracks = []

        # extract all audio segments from audio source splitting where a silince was previously detected
        for start, end in silences:
            try:
                clip_len = end - last
                # if clip last less than 5000 ms it doesn't split
                if clip_len > 5000:
                    # extract an audio segment from the source and add 0.5 s of silence at start and at the end of the segment for better transcription
                    audio_segment = AudioSegment.silent(
                        500) + audio_file[last:end] + AudioSegment.silent(500)
                    tracks.append(audio_segment)
                    last = end
            except:
                pass
        print('Done')
        #os.remove(silence_file)
        return tracks

    def extract_audio(self):
        video = mp.VideoFileClip(self.video_name)
        print('Extracting audio...')
        video.audio.write_audiofile(self.audio_file_name,bitrate='50k')

    def transcribe_tracks(self, tracks, text_file_name):
        # initialize the recogniser
        r = sr.Recognizer()
        text = ''

        # transcribe all audio segments
        for track in tracks:
            if self.loop is False:
                break
            # Create a temp file from the audio segment
            f = text_file_name.replace('.txt', 'temp.wav')
            track.export(f, format='wav')
            with sr.AudioFile(f) as source:
                audio = r.record(source)
                # Gets transcription of the audio segment
                try:
                    # try to transcribe from google server
                    r_text = r.recognize_google(audio, language=LANGUAGE)
                    # Append a new transcribed line of text to the transcription
                    text += '\n' + r_text
                    with open(text_file_name,'w') as file:
                        file.write(text)
                    print(r_text)
                    self.text_viewer.setText(r_text)
                except:
                    # notify error
                    print('ERROR')
            # delete temp file
            os.remove(f)

    def transcribe(self):
        """ Transcribe a video in a text file and return text file name """
        self.audio_file_name = self.video_name.replace('.mp4', '.wav').replace(' ','').strip()
        # load mp4 ad extract wav track
        print('Loading video...')
        # create audio file id doesn't exists
        # if not os.path.isfile(audio_file_name):
        #    open(audio_file_name, 'w')
        self.extract_audio()
        # transcript audio
        print('Starting transcription...')
        # set .txt file name to video source name
        self.text_file_name = self.video_name.replace('.mp4', '.txt')
        print('Writing text to {}'.format(self.text_file_name))
        tracks = self.split_audio()
        self.transcribe_tracks(tracks, self.text_file_name)
        os.remove(self.audio_file_name)
        # end transcription
        print('\ntranscpription terminated')
        
