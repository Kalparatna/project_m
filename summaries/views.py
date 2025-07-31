import os
import re
from django.shortcuts import render, redirect
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.0-flash')

# Home page
def index(request):
    return render(request, "summaries/index.html")

# Process video URL and generate transcript
def generate_summary(request):
    if request.method == "POST":
        youtube_url = request.POST.get("youtube_url")
        summary_type = request.POST.get("summary_type", "Concise")
        summary_length = int(request.POST.get("summary_length", 30))

        if youtube_url:
            try:
                video_id = youtube_url.split('v=')[1].split('&')[0] if 'youtube.com' in youtube_url else youtube_url.split('youtu.be/')[1]
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
                transcript_text = " ".join([item['text'] for item in transcript])

                # Generate summary using Generative AI
                system_prompt = f"""
                You are an expert in summarizing educational content.
                Create a {summary_type.lower()} summary that is approximately {summary_length}% of the original length.
                Focus on key educational points and maintain clarity.

                Make the summary clear and well-structured.
                """
                response = model.generate_content(transcript_text + system_prompt)

                if response and hasattr(response, "text"):
                    summary = response.text


                    return render(
                        request,
                        "summaries/summaries.html",
                        {
                            "summary": summary,
                            "youtube_url": youtube_url,
                            "summary_type": summary_type,
                            "summary_length": summary_length,
                        },
                    )
                else:
                    return render(request, "summaries/error.html", {"error": "Error generating summary."})
            except Exception as e:
                error_message = f"Error fetching transcript: {str(e)}"
                return render(request, "summaries/error.html", {"error": error_message})
        else:
            return render(request, "summaries/error.html", {"error": "Invalid YouTube URL."})
    else:
        return redirect("index")
