import re
import subprocess
import json

class YouTubeSummarizer:
    def __init__(self, model):
        self.model = model

    def _extract_id(self, url: str):
        for pattern in [r"(?:v=|\/)([0-9A-Za-z_-]{11})", r"youtu\.be\/([0-9A-Za-z_-]{11})"]:
            m = re.search(pattern, url)
            if m:
                return m.group(1)
        return None

    def _fetch_transcript(self, video_id: str) -> str:
        try:
            # Try youtube-transcript-api first
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript = transcript_list.find_transcript(['en', 'hi', 'en-IN'])
            except Exception:
                transcript = next(iter(transcript_list))
            segs = transcript.fetch()
            return " ".join(
                s['text'] if isinstance(s, dict) else s.text
                for s in segs
            )
        except Exception:
            pass

        try:
            # Fallback: use yt-dlp to get video info and description
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-playlist',
                 f'https://www.youtube.com/watch?v={video_id}'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                description = data.get('description', '')
                title = data.get('title', '')
                uploader = data.get('uploader', '')
                if description:
                    return f"Title: {title}\nBy: {uploader}\n\nDescription:\n{description}"
                else:
                    return f"Title: {title}\nBy: {uploader}\n\nNo transcript or description available."
        except Exception as e:
            pass

        raise ValueError(
            "Could not fetch transcript. "
            "Make sure the video has captions enabled."
        )

    def _chunk(self, text: str, max_chars: int = 8000) -> list:
        words = text.split()
        chunks, current = [], []
        for word in words:
            current.append(word)
            if len(" ".join(current)) >= max_chars:
                chunks.append(" ".join(current))
                current = []
        if current:
            chunks.append(" ".join(current))
        return chunks

    def summarize(self, url: str, detail_level: str = "Standard") -> str:
        vid_id = self._extract_id(url)
        if not vid_id:
            raise ValueError("Invalid YouTube URL.")

        transcript = self._fetch_transcript(vid_id)
        chunks = self._chunk(transcript)

        length_map = {
            "Brief":    "in 3-5 bullet points",
            "Standard": "in 2-3 short paragraphs",
            "Detailed": "with Introduction, Key Points, and Conclusion",
        }
        length_inst = length_map.get(detail_level, "in 2-3 paragraphs")

        if len(chunks) == 1:
            prompt = f"Summarize this YouTube video content {length_inst}.\n\nContent:\n{transcript[:12000]}"
            return self.model.generate_content(prompt).text

        partials = []
        for chunk in chunks:
            p = f"Summarize this part in 3-5 sentences:\n\n{chunk}"
            partials.append(self.model.generate_content(p).text)
        combined = "\n\n".join(partials)
        reduce_prompt = f"Combine these into one summary {length_inst}.\n\nPartials:\n{combined}"
        return self.model.generate_content(reduce_prompt).text