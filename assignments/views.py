# assignments/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import ResourceForm
from datetime import datetime
import os
import google.generativeai as genai
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the model
model = genai.GenerativeModel('gemini-1.0-flash')

def generate_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            # Get form data
            subject = form.cleaned_data['subject']
            difficulty = form.cleaned_data['difficulty']
            subtopics = form.cleaned_data['subtopics']
            resource_type = form.cleaned_data['resource_type']
            education_level = form.cleaned_data['education_level']
            
            # Generate the resource based on the selected type
            prompt = create_prompt(resource_type, subject, difficulty, subtopics, education_level, form)
            response = model.generate_content(prompt)
            result = response.text
            result_cleaned = result.replace('*', '')

            # Add generated resource to session
            if 'resource_history' not in request.session:
                request.session['resource_history'] = []
            request.session['resource_history'].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "resource_type": resource_type,
                "subject": subject,
                "difficulty": difficulty,
                "content": result
            })
            return render(request, 'assignments/result.html', {'result': result_cleaned, 'form': form})
    else:
        form = ResourceForm()

    return render(request, 'assignments/index.html', {'form': form})


def create_prompt(resource_type, subject, difficulty, subtopics, education_level, form):
    # Initialize base prompt
    prompt = f"""Create a {resource_type} for {subject} at {education_level} level.
    Difficulty: {difficulty}
    Topics: {subtopics}
    """

    # Add resource-specific parameters to the prompt
    if resource_type == "Practice Exam":
        question_count = form.cleaned_data['question_count']
        time_limit = form.cleaned_data['time_limit']
        question_types = form.cleaned_data['question_types']
        prompt += f"""
        Generate {question_count} questions including {', '.join(question_types)}.
        Time Limit: {time_limit} minutes
        
        """
    elif resource_type == "Flashcards":
        card_count = form.cleaned_data['card_count']
        include_examples = form.cleaned_data['include_examples']
        prompt += f"""
        Create {card_count} flashcards with:
        {'Example usage' if include_examples else ''}
        """
    # Add other resource types (Study Notes, Mind Map, Quiz) similarly
    return prompt

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap

def download_pdf(request):
    # Get content to be included in the PDF
    resource_content = request.GET.get('content', 'Default Content Here')

    # Create PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Set font and title
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, 750, "AI-Generated Study Resource")

    # Set text parameters
    margin = 72  # Left margin for content
    max_width = 480  # Max width for text
    line_height = 14  # Line height for spacing between lines

    # Create a text object for the content
    text_object = p.beginText(margin, 730)  # Starting position for text
    text_object.setFont("Helvetica", 10)
    text_object.setTextOrigin(margin, 730)

    # Wrap the content using textwrap to handle long lines
    wrapped_lines = textwrap.wrap(resource_content, width=70)  # Wrap text at 70 characters

    y_position = 730  # Y-position for the text
    for line in wrapped_lines:
        # Check if content exceeds current page height and add new page if needed
        if y_position - line_height < 50:
            p.showPage()
            y_position = 750  # Reset to top of the new page
            text_object = p.beginText(margin, y_position)
            text_object.setFont("Helvetica", 10)
        
        # Add line of text to the PDF
        text_object.textLine(line)
        y_position -= line_height  # Move to the next line

    # Draw the wrapped text to the PDF
    p.drawText(text_object)
    p.showPage()  # Close the current page
    p.save()

    # Send the PDF as a response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="generated_resource.pdf"'
    return response
