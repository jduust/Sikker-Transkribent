import os
from glob import glob
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
import numpy as np
from faster_whisper import WhisperModel
from datetime import timedelta
from tqdm import tqdm
import soundfile as sf
from pydub import AudioSegment

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

encoder = VoiceEncoder()
whisper_model = WhisperModel("large-v3", device="cpu")
SAMPLING_RATE = 16000

def format_timestamp(seconds, for_srt=False):
    # for_srt changes to , and ms
    if for_srt:
        ms = int((seconds - int(seconds)) * 1000)
        t = str(timedelta(seconds=int(seconds)))
        if len(t.split(":")) == 2:  # if format is MM:SS
            t = "00:" + t
        return f"{t},{ms:03d}"
    else:
        return str(timedelta(seconds=int(seconds)))

def load_audio(file_path):
    # Load audio, support multiple formats and resample to 16kHz mono wav array
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(SAMPLING_RATE).set_channels(1)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
    return samples

def cluster_speakers(wav, segments, max_speakers=6):
    # Extract embeddings per segment
    segment_embeddings = []
    valid_segments = []

    for seg in segments:
        start, end = seg.start, seg.end
        start_sample = int(start * SAMPLING_RATE)
        end_sample = int(end * SAMPLING_RATE)
        audio_slice = wav[start_sample:end_sample]
        if len(audio_slice) < SAMPLING_RATE // 2:
            continue  # too short segment
        embed = encoder.embed_utterance(audio_slice)
        segment_embeddings.append(embed)
        valid_segments.append(seg)

    if len(segment_embeddings) == 0:
        return []

    # Try clustering for different speaker counts, pick best silhouette score
    best_score = -1
    best_labels = None
    best_n = 1
    for n_speakers in range(1, min(max_speakers, len(segment_embeddings)) + 1):
        clustering = AgglomerativeClustering(n_clusters=n_speakers)
        labels = clustering.fit_predict(segment_embeddings)
        if n_speakers == 1:
            score = 0  # silhouette score can't be computed with 1 cluster
        else:
            try:
                score = silhouette_score(segment_embeddings, labels)
            except Exception:
                score = -1
        if score > best_score:
            best_score = score
            best_labels = labels
            best_n = n_speakers

    return list(zip(valid_segments, best_labels)), best_n

def merge_short_segments(clustered_segments, min_duration=1.0):
    # Merge consecutive segments from the same speaker shorter than min_duration
    if not clustered_segments:
        return []

    merged = []
    current_seg, current_speaker = clustered_segments[0]
    current_start = current_seg.start
    current_end = current_seg.end
    current_text = current_seg.text

    for seg, speaker in clustered_segments[1:]:
        duration = current_end - current_start
        if speaker == current_speaker and duration < min_duration:
            # merge
            current_end = seg.end
            current_text += " " + seg.text
        else:
            # save previous
            merged.append((current_start, current_end, current_speaker, current_text.strip()))
            current_start = seg.start
            current_end = seg.end
            current_speaker = speaker
            current_text = seg.text
    # append last
    merged.append((current_start, current_end, current_speaker, current_text.strip()))
    return merged

def write_txt(out_path, merged_segments):
    with open(out_path, "w", encoding="utf-8") as f:
        for start, end, speaker, text in merged_segments:
            start_s = format_timestamp(start)
            end_s = format_timestamp(end)
            f.write(f"[{start_s} - {end_s}] Speaker {speaker + 1}: {text}\n")

def write_srt(out_path, merged_segments):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, (start, end, speaker, text) in enumerate(merged_segments, start=1):
            start_s = format_timestamp(start, for_srt=True)
            end_s = format_timestamp(end, for_srt=True)
            f.write(f"{i}\n")
            f.write(f"{start_s} --> {end_s}\n")
            f.write(f"Speaker {speaker + 1}: {text}\n\n")

def process_file(audio_path):
    filename = os.path.basename(audio_path)
    print(f"\nProcessing {filename}...")

    # Load audio for embeddings
    wav = load_audio(audio_path)

    segments, info = whisper_model.transcribe(audio_path, language="da")
    whisper_segments = list(segments)

    clustered_segments, n_speakers = cluster_speakers(wav, whisper_segments)
    if not clustered_segments:
        print("No valid segments found for diarization!")
        return

    print(f"Detected {n_speakers} speakers.")

    merged_segments = merge_short_segments(clustered_segments)

    # Show progress
    for start, end, speaker, text in tqdm(merged_segments, desc="Saving segments"):
        pass  # just to have tqdm progress bar

    # Write TXT and SRT outputs
    base_name = os.path.splitext(filename)[0]
    write_txt(os.path.join(OUTPUT_FOLDER, base_name + "_transcript.txt"), merged_segments)
    write_srt(os.path.join(OUTPUT_FOLDER, base_name + "_transcript.srt"), merged_segments)

    print(f"Saved transcript and subtitles for {filename}")

def main():
    audio_files = glob(os.path.join(INPUT_FOLDER, "*.*"))
    supported_ext = {".mp3", ".wav", ".m4a"}
    audio_files = [f for f in audio_files if os.path.splitext(f)[1].lower() in supported_ext]

    if not audio_files:
        print(f"No supported audio files found in {INPUT_FOLDER}")
        return

    for audio_path in tqdm(audio_files, desc="Files", unit="file"):
        process_file(audio_path)

    print("\n✅ All files processed!")

if __name__ == "__main__":
    main()
