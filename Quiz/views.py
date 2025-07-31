from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import MCQTopic, MCQ
import json
import google.generativeai as genai
from django.conf import settings
from dotenv import load_dotenv
import os
import time
from django.urls import reverse  # Import reverse

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

import re

def generate_mcqs(topic, num_questions, retries=3):
    prompt = (
        f"Generate {num_questions} multiple-choice questions (MCQs) on the topic '{topic}'. "
        "Each question should have four options, with one correct answer, formatted as follows:\n"
        "{\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"question\": \"Question text\",\n"
        "      \"options\": [\"Option 1\", \"Option 2\", \"Option 3\", \"Option 4\"],\n"
        "      \"correct_answer\": \"Option 1\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            print("\n\n🌟 Raw Gemini Response:")
            print(response.text)  # Debugging output
            
            # ✅ Extract only JSON part using regex
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                json_content = match.group(0)
                mcqs = json.loads(json_content)
                return mcqs['questions']
            else:
                print("🚨 No valid JSON object found in response.")
        
        except json.JSONDecodeError as e:
            print("🚨 Error parsing JSON response:", e)
        
        except Exception as e:
            print("❌ An error occurred:", e)
        
        time.sleep(2)
    
    return None


def quiz_home(request):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return render(request, 'quiz/error.html', {"error": "API key not configured correctly."})

    if request.method == 'POST':
        topic = request.POST.get('topic')
        num_questions = int(request.POST.get('num_questions'))  # Get the number of questions

        if topic:
            # Generate quiz questions
            questions = generate_mcqs(topic, num_questions)
            if not questions:
                return render(request, 'quiz/error.html', {"error": "Failed to generate MCQs."})

            # Debug: Print the generated questions to inspect the structure
            print("Generated Questions:", questions)
            
            # Save the topic with the number of questions
            mcq_topic = MCQTopic.objects.create(title=topic, num_questions=num_questions)

            # Store each MCQ
            for index, question in enumerate(questions, start=1):
                # Ensure the question has four options
                options = question.get('options', [])
                if len(options) < 4:
                    # Handle cases with fewer than four options (skip or pad with "N/A")
                    while len(options) < 4:
                        options.append("N/A")
                
                try:
                    MCQ.objects.create(
                        topic=mcq_topic,
                        question_no=index,
                        question=question.get('question', 'No question provided'),
                        option_1=options[0],
                        option_2=options[1],
                        option_3=options[2],
                        option_4=options[3],
                        correct_answer=question.get('correct_answer', 'N/A')
                    )
                except IndexError:
                    print(f"Error with question {index}: {question}")
                    return render(request, 'quiz/error.html', {"error": f"Error storing MCQ {index}"})
            
            # Redirect to the quiz page for the newly created topic
            messages.success(request, 'MCQs generated and stored successfully! Now take the quiz.')
            return redirect(reverse('quiz:quiz_start', args=[mcq_topic.id])) 
            
    return render(request, 'quiz/index.html')

def quiz_start(request, topic_id):
    mcq_topic = get_object_or_404(MCQTopic, pk=topic_id)
    return render(request, 'quiz/start_quiz.html', {'topic': mcq_topic})

def take_quiz(request, topic_id):
    # Fetch the selected topic and its associated MCQs
    mcq_topic = get_object_or_404(MCQTopic, id=topic_id)
    mcqs = MCQ.objects.filter(topic=mcq_topic)

    if request.method == 'POST':
        # Initialize score
        score = 0
        total_questions = mcqs.count()

        # Loop through each MCQ and check the submitted answer
        for mcq in mcqs:
            selected_answer = request.POST.get(f'mcq_{mcq.id}')
            if selected_answer == mcq.correct_answer:
                score += 1
        
        # Display the score and results
        messages.success(request, f'You scored {score} out of {total_questions}!')
        return render(request, 'quiz/quiz_results.html', {
            'mcq_topic': mcq_topic,
            'mcqs': mcqs,
            'score': score,
            'total_questions': total_questions
        })
    
    return render(request, 'quiz/quiz_form.html', {
        'mcq_topic': mcq_topic,
        'mcqs': mcqs
    })