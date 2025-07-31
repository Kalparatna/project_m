from django.shortcuts import render, redirect
from django.http import JsonResponse
import google.generativeai as genai
from dotenv import load_dotenv
from .models import LearningModule, ChatHistory , app_topics # Make sure to import your new ChatHistory model
import os
from django import template
import markdown2

from django.shortcuts import render
from django.http import HttpResponse
from .models import LearningModule  # Import your models
from fpdf import FPDF  # For generating PDF
import io 

# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Load environment variables
load_dotenv()

# Set up the API key for the genai package
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def home(request):
    return render(request, 'home.html') 

def services(request):
    return render(request, 'Services.html')

def generate_learning_modules(topic):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = (
       f"Generate five learning modules for the topic '{topic}'. "

    )
    
    response = model.generate_content(prompt)

    modules = [line.strip() for line in response.text.split("\n") if " - " in line]

    LearningModule.objects.filter(topic=topic).delete()
    for module in modules[:5]:
        title, description = module.split(" - ", 1)
        title = title.strip().strip("*") 

        LearningModule.objects.create(
            topic=topic,
            title=title.strip(),
            description=description.strip()
        )

    return modules[:5]

# Index view
def index(request):
    error = None
    topic = ""

    if request.method == "POST":
        topic = request.POST.get("topic")
        if topic:
            try:
                app_topics.objects.create(topic_name=topic)

                return redirect('modules', topic=topic)  
            except Exception as e:
                error = "Error generating modules: " + str(e)
        else:
            error = "Please enter a valid topic."

    return render(request, 'index.html', {'topic': topic, 'error': error})


# Modules view
def modules(request, topic):
    modules = []
    error = None

    if topic:
        try:
            modules = generate_learning_modules(topic)
            request.session['modules'] = modules  
        except Exception as e:
            error = "Error generating modules: " + str(e)

    return render(request, 'modules.html', {'modules': modules, 'topic': topic, 'error': error})

# Choose tutor and chat
def get_gemini_response(question, character, chat_history, level):
    model = genai.GenerativeModel('gemini-1.0-flash')
    
    # Character roleplay instructions
    instructions = {
       'Shah Rukh Khan': """
        You are Shah Rukh Khan, a legendary Indian actor and now an AI tutor. You respond in a blend of Hindi and English, 
        just like you would in your movies or interviews, with a touch of drama, charm, and wit. Use casual phrases like 'Are yaar', 
        'Main hoon na', 'Dil se', 'Kuch kuch hota hai', or 'Don ko pakadna mushkil hi nahi...' 🔥✨.
        When explaining, you mix both languages seamlessly  

        Teach with passion and flair, as if you're giving a motivational speech in a film. 🎥✨.And dont answer other topic except related to these modules generated
        """,

        'Virat Kohli': """
        You are Virat Kohli, the legendary Indian cricketer. Respond in a blend of English and Hindi . Use motivational phrases 
        like 'Never give up,' 'Chase your dreams,' or 'Teamwork is key.' 💪🏏. When explaining, mix both languages seamlessly 
        (e.g., 'Yeh cricket hai, kuch bhi ho sakta hai,' or 'This is a game of patience and precision'). 🏏

        Teach with passion and intensity, as if you're giving a pep talk to your team. Use references from your cricket career to make 
        concepts relatable and inspiring. 🏆🔥 Stay conversational, like discussing strategies with a teammate, and make the learner feel like a champion! 🏅👊
        """,

        'Doremon': """
        You are Doraemon,A cartoon Charecter, and lovable blue robot from the future. You love to eat Dora cakes,Mii-chan is cat , which is your frined. Respond in a playful and friendly tone, mixing Hindi and English. Use fun phrases like 'I'll do my best!' or 'Let's go on an adventure!' 🤖🌍. When explaining, blend both languages seamlessly (e.g., 'Kore wa sugoi ne!' or 'This is amazing!', Chalo dosto adventure par chalte hai, This is just like my Gadgets). 😲✨
        Teach with a sense of wonder and excitement, as if you're exploring a new world with your friends. Use references from your adventures to make concepts relatable and fun.Give examples of Nobita and your Gadgets 🌈🌟 Stay conversational, like discussing gadgets with Nobita, and make the learner feel like a part of your world! 🐱🚀
                """,

        'Steve Jobs': """
        You are Steve Jobs, the visionary co-founder of Apple. Respond in a confident, charismatic manner, using simple, direct language. 
        Use phrases like 'Think different,' 'Simplicity is the ultimate sophistication,' or 'Innovation distinguishes between a leader and a follower.' 💡📱.
        Focus on clarity and precision (e.g., 'It's not about the technology, it's about the experience' or 'Design is not just how it looks, it's how it works'). 🎨⚙️
         
        Teach with passion and conviction, and inspire the learner to think creatively. 🧠🚀
        """,

        'Cristiano Ronaldo': """
        You are Cristiano Ronaldo, the legendary football player. Respond in a confident, determined manner, using English only. 
        Use empowering expressions like 'I'm the best!' and 'Let's win!' 🏆⚽ When explaining, focus on clarity and motivation 
        (e.g., 'Success comes from hard work and dedication'). 💪🏅
       
        Teach with intensity and drive, as if you're training for a match. Make the learner feel like they can achieve greatness! 🚀🔥
        """
    }

    character_instruction = instructions.get(character, "")
    
    # Prepare chat history for the prompt
    history_prompt = "\n".join([f"User: {chat.message}\n{chat.tutor_id}: {chat.response}" for chat in chat_history])
    
    # Determine the response style based on the level
    level_prompt = ""
    if level == "beginner":
        level_prompt = "Please explain this concept in a simple and easy-to-understand manner with more detailed description, suppose that person has no prior knowledge."
    elif level == "intermediate":
        level_prompt = "Provide a detailed explanation, assuming that person has prior knowledge of the topic."
    elif level == "advanced":
        level_prompt = "Give an in-depth analysis and discussion and give higher-level knowledge concepts, suitable for someone who is well-versed in the subject."

    # Create the full prompt with history and level instructions
    full_prompt = f"{character_instruction}\n{history_prompt}\n{level_prompt}\nUser: {question}\n"
    
    # Get the response from Gemini API
    response = model.generate_content(full_prompt)

    # Check if response has a 'text' attribute
    response_text = response.text if hasattr(response, 'text') else str(response)

    # Convert the response to HTML
    response_html = markdown2.markdown(response_text)

    # Save the chat history
    ChatHistory.objects.create(
        user_id=1,  # Replace with actual user ID from request
        tutor_id=character,
        message=question,
        response=response_html
    )
    
    # Adding emojis to the final output if not included in the response
    emojis = {
        'Shah Rukh Khan': '🎬',
        'Virat Kohli': '🏆',
        'Doremon': '💡',
        'Steve Jobs': '📱',
        'Cristiano Ronaldo': '⚽'
    }
    
    emoji_string = emojis.get(character, "")
    final_response = f"{response_html} {emoji_string}"
    
    return final_response


def character_selection(request):
    if request.method == "POST":
        character = request.POST.get("character")
        return redirect('level_selection', character=character)  # Redirect to level selection

    return render(request, 'character.html')  # Replace with your actual template


def level_selection(request, character):
    if request.method == "POST":
        level = request.POST.get("level")
        return redirect('chat_with_tutor', character=character, level=level)

    return render(request, 'level_selection.html', {'character': character})


register = template.Library()

@register.filter
def remove_stars(value):
    return value.replace('**', '')


def chat_with_tutor(request, character,level):
    response = ""
    user_input = ""  # Initialize user_input

    modules = request.session.get('modules', [])  # Get modules from session
    
    # Get chat history for the selected tutor
    chat_history = ChatHistory.objects.filter(tutor_id=character).order_by('timestamp')

    # Clear chat history if the clear button is clicked
    if request.method == "POST":
        if 'clear_chat' in request.POST:
            # Clear the chat history in the session or database as needed
            ChatHistory.objects.filter(tutor_id=character).delete()  # Delete all chat history for this tutor
            chat_history = []  # Reset chat history in the view
        else:
            user_input = request.POST.get("user_input")  # Get user input
            response = get_gemini_response(user_input, character, chat_history, level)  # No need to store chat again here

            # Ensure response is a string and apply replace
            if isinstance(response, str):
                response = response.replace('**', '')
            else:
                response = str(response)

    # Clean the modules for the current session by removing stars
    cleaned_modules = []
    for module in modules:
        if isinstance(module, dict):
            # If it's a dictionary, access title and description
            cleaned_modules.append({
                'title': remove_stars(module.get('title', '')),
                'description': remove_stars(module.get('description', ''))
            })
        else:
            # If it's a string, treat it as the title with an empty description
            cleaned_modules.append({
                'title': remove_stars(module),
                'description': ''
            })


    return render(request, 'chat.html', {
        'response': response,
        'user_input': user_input,  # Pass user_input to the template
        'character': character,
        'modules': cleaned_modules,  
        'chat_history': chat_history ,
         'level': level,
    })        




# Function to generate MCQs using Gemini API
def generate_mcqs(topic):
    prompt = (
        f"Generate 10 multiple-choice questions (MCQs) on the topic '{topic}'. "
        "Each question should have four options, with one correct answer, formatted as follows:\n"
        "{\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"question\": \"Question text\",\n"
        "      \"options\": [\"Option 1\", \"Option 2\", \"Option 3\", \"Option 4\"],\n"
        "      \"correct_answer\": \"Option 1\"\n"
        "    }\n"
        "  ]\n"
        "} "
    )
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    
    try:
        mcqs = json.loads(response.text)
        return mcqs['questions']
    except json.JSONDecodeError as e:
        print("Error parsing JSON response:", e)
        print("Raw response:", response.text)
        return None

# Django form to handle topic input
class QuizForm(forms.Form):
    topic = forms.CharField(max_length=255, label='Enter Topic')

# View for generating quiz
def quiz_view(request):
    questions = []
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            questions = generate_mcqs(topic)
            if questions is None:
                return HttpResponse("Failed to generate MCQs. Check server logs for details.")
    else:
        form = QuizForm()

    return render(request, 'quiz.html', {'form': form, 'questions': questions})

# View to handle quiz submission (result calculation)
def quiz_result_view(request):
    if request.method == 'POST':
        total = len(request.POST) - 1  # minus 1 for CSRF token
        score = 0
        for key, value in request.POST.items():
            if key.startswith('question_'):
                correct_answer = request.POST.get(f'correct_answer_{key}')
                if value == correct_answer:
                    score += 1
        
        return render(request, 'result.html', {'score': score, 'total': total})
    return redirect('quiz')
