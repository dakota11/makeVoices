#!/usr/bin/python3
 
import json
import os
import re
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs


def read_and_filter_file():
    # Ask for the file name
    file_name = input("Enter the file name (without extension): ") + ".txt"
    
    lines_data = []
    
    try:
        # Open the file for reading
        with open(file_name, 'r') as file:
            # Loop through each line in the file
            for line in file:
                line = line.strip()
                if not line or line.startswith(('*', '_', '>', '{')):
                    continue
                # Check if the line does not start with *, _, >, or {
                if not line.startswith(('*', '_', '>', '{', '-')):
                    line_data = {}
                    if line.startswith('@'):
                        parts = line.split(' ', 1)
                        speaker = parts[0][1:]
                        text = parts[1] if len(parts) > 1 else ''
                        line_data['speaker'] = speaker
                        line_data['text'] = text
                    else:
                        line_data['speaker'] = None
                        line_data['text'] = line
                    
                    lines_data.append(line_data)
        
        # Convert the list of dictionaries to a JSON array
        json_output = json.dumps(lines_data, indent=4)
        return json_output, file_name[:-4]

    except FileNotFoundError:
        return f"The file {file_name} does not exist.", None


def process_json_string(json_string, output_subdirectory):
    # Parse the JSON string
    data = json.loads(json_string)
    
    # Process each item in the JSON array
    for item in data:
        # Perform some action on each item
        text_to_speech(item, "ba50a4987cbe6d25581236da9a1f67aa", output_subdirectory)  # Example action: print each item
    
    # Return the processed data
    return data


def text_to_speech(json_data, api_key, output_subdirectory):

    voiceId =  get_id_by_name(json_data.get("speaker"))
    # print(json_data)
    # return

    # Initialize the ElevenLabs client
    client = ElevenLabs(api_key=api_key)

    # Set voice settings (customize as needed)
    # voice_settings = VoiceSettings(
    #     stability=0.75,  # Example setting
    #     similarity_boost=0.75,  # Example setting
    # )

    # Make the API request to convert text to speech
    response = client.text_to_speech.convert(
        voice_id=voiceId,  # Replace with your desired voice ID
        text=json_data['text'],
        # model_id="eleven_turbo_v2",
         model_id="eleven_multilingual_v2", 
        # voice_settings=voice_settings,
    )

    # Determine the final output directory
    if json_data.get('speaker'):
        output_directory = os.path.join('output', output_subdirectory, json_data['speaker'])
    else:
        output_directory = os.path.join('output', output_subdirectory)
    
    # Ensure the output subdirectory exists
    os.makedirs(output_directory, exist_ok=True)

    # Generate filename from the text content
    text_content = json_data['text']
    # Replace spaces with dashes, remove non-alphanumeric characters, convert to lowercase
    filename_base = re.sub(r'[^a-z0-9]+', '-', text_content.lower()).strip('-')
    # Trim to 25 characters
    filename_base = filename_base[:25]

    # Save the returned audio file
    audio_filename = os.path.join(output_directory, f"{filename_base}.mp3")
    with open(audio_filename, 'wb') as audio_file:
        for chunk in response:
            if chunk:
                audio_file.write(chunk)

    print(f"Audio file saved to {audio_filename}")

def get_id_by_name(name):
    ids = {
        "waitress": "WhPfBSRa3g76IU7ZamZ7",  # Rebecca - wide emotional range
        "winter": "zcF0pYJOwZDTyML02zQ7",    # Benjamin
        "snitch": "cLyMLuX943bp02WVe9st",# Alexander
    }
    
    if name is None:
        return "tnSpp4vdxKPjI9w0GnoV"  # Hope - upbeat and clear
    
    return ids.get(name, "ID not found")


if __name__ == "__main__":
    json_result, output_subdirectory = read_and_filter_file()
    if output_subdirectory:
        process_json_string(json_result, output_subdirectory)
