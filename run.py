import os
import shutil
import Scripts.transcriber as transcriber

source_folder = 'source/'
dest_folder = 'transcriptions/'
elaborated_folder = 'elaborated_videos/'

# Create source directory if doesn't exist
if not os.path.exists(source_folder):
    os.mkdir(source_folder)
    print('Please place your videos in source folder')

# Create transcriptions directory if doesn't exist
if not os.path.exists(dest_folder):
    os.mkdir(dest_folder)
    print('You will find transcriptions text in transcriptions folder')

# Create elaborated directory if doesn't exist
if not os.path.exists(elaborated_folder):
    os.mkdir(elaborated_folder)

# Load all videos in source folder
source_videos = os.listdir(source_folder)

# Notify user that source is empty
if len(source_videos)==0:
    print('Source folder is empty')

# Iterate each video
for video in source_videos:
    # Video must be .mp4 format
    if video.find('.mp4')!=-1:
        # Transcribe
        output_filename =  transcriber.transcribe(video, source_folder)
        # Move transcribed text in destination folder
        shutil.move(output_filename, dest_folder + output_filename)
        # Move elaborated video to elaborated folder
        shutil.move(source_folder + video, elaborated_folder + video)

# Delete temporary files
try:
    os.remove('track.wav')
    os.remove('temp.wav')
    os.remove('silence.txt')
except:
    pass

print('\nAll videos has been transcripted')
