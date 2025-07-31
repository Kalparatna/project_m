import os
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from dotenv import load_dotenv
import google.generativeai as genai
from .models import StudyPlan
from markdown import markdown

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')


def index(request):
    """Render the index page."""
    return render(request, 'studyplanner/index.html')


def generate_plan(request):
    """Generate the study plan and save it to the database."""
    if request.method == 'POST':
        # Get POST data
        subject = request.POST.get('subject')
        duration = request.POST.get('duration')
        difficulty_level = request.POST.get('difficulty_level')
        goal = request.POST.get('goal')
        study_hours = request.POST.get('study_hours')
        preferred_time = request.POST.getlist('preferred_time')

        # Validate required fields
        if not subject or not goal:
            return JsonResponse({"error": "Please fill in all required fields!"}, status=400)

        # Construct prompt for AI model
        prompt = f"""
        Create a detailed study plan based on the following parameters:
        Subject: {subject}
        Duration: {duration}
        Knowledge Level: {difficulty_level}
        Goals: {goal}
        Available Hours: {study_hours} hours per week
        Preferred Study Time: {', '.join(preferred_time)}
        """

        try:
            # Generate content using AI model
            response = model.generate_content(prompt)
            study_plan_text = response.text.replace("*", " ")

            # Format the study plan as HTML (e.g., converting lists and paragraphs)
            formatted_plan = study_plan_text.replace("\n", "<br>").replace("<br><br>", "</p><p>")
            formatted_plan = markdown(study_plan_text)

            # Save the study plan in the database
            study_plan_entry = StudyPlan(
                subject=subject,
                duration=duration,
                difficulty_level=difficulty_level,
                goal=goal,
                study_hours=study_hours,
                preferred_time=', '.join(preferred_time),
                study_plan=formatted_plan
            )
            study_plan_entry.save()

            # Return success response with the structured HTML
            return JsonResponse({
                "study_plan": formatted_plan,
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {e}"}, status=500)


def fetch_study_plan(request, plan_id):
    """Fetch a saved study plan from the database."""
    try:
        # Retrieve the study plan
        study_plan = StudyPlan.objects.get(id=plan_id)

        # Format for display
        formatted_plan = f"""
            <h4><strong>Study Plan for {study_plan.subject}</strong></h4>
            <ul>
                <li><strong>Study Duration:</strong> {study_plan.duration}</li>
                <li><strong>Knowledge Level:</strong> {study_plan.difficulty_level}</li>
                <li><strong>Learning Goal:</strong> {study_plan.goal}</li>
                <li><strong>Study Hours:</strong> {study_plan.study_hours} per week</li>
                <li><strong>Preferred Time:</strong> {study_plan.preferred_time}</li>
            </ul>
            <h5>Weekly Breakdown:</h5>
            <p>{study_plan.study_plan}</p>
        """
        return "done"

    except StudyPlan.DoesNotExist:
        return JsonResponse({"error": "Study plan not found!"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {e}"}, status=500)


def download_text_file(request):
    """Handle download of study plan as a text file."""
    if request.method == 'POST':
        try:
            # Parse the JSON data
            data = json.loads(request.body)
            study_plan = data.get('study_plan', None)

            if not study_plan:
                return JsonResponse({"error": "No study plan provided!"}, status=400)

            # Create a response with the content as a text file
            response = HttpResponse(study_plan, content_type='text/plain')

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {e}"}, status=500)
