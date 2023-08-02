import streamlit as st
from PIL import Image
import exifread
import tempfile
import os
from moviepy.editor import VideoFileClip
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# Function to extract metadata from the image file
def get_metadata(image_file_path):
    with open(image_file_path, "rb") as f:
        tags = exifread.process_file(f)
    taken_date = tags.get('EXIF DateTimeOriginal', None)
    taken_location = tags.get('GPS GPSLatitude', None), tags.get('GPS GPSLongitude', None)
    return taken_date, taken_location

# Function to extract GPS metadata from video file
def get_video_metadata(video_file_path):
    parser = createParser(video_file_path)
    metadata = extractMetadata(parser)
    taken_date = metadata.get('creation_date', None)

    taken_location = None, None
    for line in metadata.exportPlaintext():
        if 'GPS latitude' in line.lower():
            taken_location = line.split(':')[-1].strip(), taken_location[1]
        elif 'GPS longitude' in line.lower():
            taken_location = taken_location[0], line.split(':')[-1].strip()

    return taken_date, taken_location

# Function to convert .mov to .mp4 using moviepy
def convert_mov_to_mp4(mov_file_path):
    mp4_path = os.path.splitext(mov_file_path)[0] + '.mp4'
    video_clip = VideoFileClip(mov_file_path)
    video_clip.write_videofile(mp4_path, codec="libx264")
    video_clip.close()
    return mp4_path

st.title("Photo & Video Metadata Viewer")
st.write("Upload your photos and videos and see their metadata.")

# File uploader
uploaded_file = st.file_uploader("Choose a photo or video...", type=["jpg", "jpeg", "png", "mp4", "mov"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded content
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_filename = tmp_file.name
        tmp_file.write(uploaded_file.read())

    file_type = uploaded_file.type.split('/')[0]
    if file_type == "image":
        # Display uploaded image and metadata
        image = Image.open(tmp_filename)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        taken_date, taken_location = get_metadata(tmp_filename)
        st.write("Metadata:")
        st.write(f"Taken Date: {taken_date}")
        if taken_location[0] is not None and taken_location[1] is not None:
            st.write(f"Taken Location: Latitude {taken_location[0]}, Longitude {taken_location[1]}")
        else:
            st.write("Location information not available.")

    elif file_type == "video":
        # Handle .mov videos
        if uploaded_file.type == "video/quicktime":
            st.warning("Converting .mov video to .mp4. Please wait...")
            tmp_filename = convert_mov_to_mp4(tmp_filename)

        # Display uploaded video and metadata
        st.video(tmp_filename, format='video/mp4')
        taken_date, taken_location = get_video_metadata(tmp_filename)

        duration = VideoFileClip(tmp_filename).duration
        resolution = VideoFileClip(tmp_filename).size

        st.write("Metadata:")
        st.write(f"Taken Date: {taken_date}")
        if taken_location[0] is not None and taken_location[1] is not None:
            st.write(f"Taken Location: Latitude {taken_location[0]}, Longitude {taken_location[1]}")
        else:
            st.write("Location information not available.")
        st.write(f"Duration: {duration:.2f} seconds")
        st.write(f"Resolution: {resolution[0]}x{resolution[1]}")

    else:
        st.write("Unsupported file format. Please upload an image or video.")

    # Remove the temporary file after displaying the content
    os.remove(tmp_filename)
