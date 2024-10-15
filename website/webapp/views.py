from django.shortcuts import render,redirect
from . forms import NewAccountForm,LoginPageForm,AddRecord,UpdateRecord,UploadDocumentForm,RoleSelectionForm,AuthenticationForm
from django.contrib.auth.models import auth

from django.contrib.auth import authenticate

from django.contrib.auth import login as auth_login

from django.contrib.auth.decorators import login_required

from .models import UserData
from django.contrib import messages
from django.views.generic import FormView

import pytesseract
import json
import os
import PyPDF2


def home(request):

    return render(request, 'webapp/index.html')

def about(request):

    return render(request, 'webapp/about.html')

def register(request):

    form = NewAccountForm()
    if request.method == "POST":
        form = NewAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created Successfully!")
            return redirect('login')
    context = {'form':form}
    return render(request, 'webapp/register.html', context=context)



def login(request):
    form = LoginPageForm()
    if request.method == "POST":
        form = LoginPageForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
    context = {'form':form}
    return render(request, 'webapp/login.html', context=context)


def dashboard(request):
    records = UserData.objects.all()  # Fetch all saved user data
    return render(request, 'webapp/dashboard.html', {'records': records})



#Record Creation

@login_required(login_url = 'login')
def create(request):

    form = AddRecord()
    if request.method == "POST":
        form = AddRecord(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    
    context = {'form': form}
    return render(request, 'webapp/create.html', context=context)

#RecordUpdate

@login_required(login_url = 'login')
def update(request, pk):

    record = UserData.objects.get(id=pk)
    form = UpdateRecord(instance = record)
    
    if request.method == "POST":
        form = UpdateRecord(request.POST, instance=record)

        if form.is_valid():
            form.save()
            return redirect("dashboard")
        
    context = {'form':form}

    return render(request, 'webapp/update.html',context = context)



#Read/View a single Record

@login_required(login_url = 'login')
def record(request, pk):

    record = UserData.objects.get(id=pk)
    context = {'record': record}
    return render(request,'webapp/view.html',context = context)

#Delete Record
@login_required(login_url = 'login')
def delete(pk):

    record = UserData.objects.get(id=pk)
    record.delete()
   
    return redirect("dashboard")


def logout(request):

    auth.logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect("login")



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Specify path to tesseract.exe if necessary (Windows)
  # Ensure user is logged in before allowing access

def process_extracted_data(data):
    """
    Process the extracted text where each line contains a key (e.g., "Name:", "Email:") 
    followed by the value. This function will extract and structure the data.
    """
    structured_data = {}
    lines = data.split('\n')  # Split the data by lines

    # Iterate over each line and extract the relevant fields
    for line in lines:
        line = line.strip()  # Remove any leading or trailing whitespace
        if line.startswith("Name:"):
            # Extract first name and last name from "Name: John Doe"
            full_name = line.replace("Name:", "").strip()
            name_parts = full_name.split()  # Split name into parts
            if len(name_parts) >= 2:
                structured_data['first_name'] = name_parts[0]
                structured_data['last_name'] = " ".join(name_parts[1:])
            else:
                structured_data['first_name'] = full_name
                structured_data['last_name'] = ""  # Handle single name cases
        elif line.startswith("Email:"):
            structured_data['email'] = line.replace("Email:", "").strip()
        elif line.startswith("Phone:"):
            structured_data['phone'] = line.replace("Phone:", "").strip()
        elif line.startswith("Address:"):
            structured_data['address'] = line.replace("Address:", "").strip()
        elif line.startswith("City:"):
            structured_data['city'] = line.replace("City:", "").strip()
        elif line.startswith("State:"):
            structured_data['state'] = line.replace("State:", "").strip()
        elif line.startswith("Country:"):
            structured_data['country'] = line.replace("Country:", "").strip()

    # Convert the structured_data dictionary into a list of dictionaries for table display
    return [structured_data] if structured_data else []


def upload(request):
    structured_data = None

    # Handling the upload and text extraction
    if request.method == 'POST' and 'upload_button' in request.POST:
        form = UploadDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()  # Save the uploaded file to the Document model
            file_path = document.file.path  # Get the absolute file path

            if os.path.exists(file_path):
                try:
                    if file_path.endswith('.pdf'):
                        extracted_text = extract_pdf_data(file_path)
                        print(f"Extracted Text from PDF: {extracted_text}")

                        # Process the extracted text into structured data
                        structured_data = process_extracted_data(extracted_text)
                        print(f"Structured Data: {structured_data}")  # Debugging
                    else:
                        print("Unsupported file format")
                except Exception as e:
                    print(f"Error during file processing: {e}")
                    return render(request, 'webapp/error.html', {'error': str(e)})
            else:
                print("File does not exist")
                return redirect('error_view')

    # Handling the save action (when "Save to Dashboard" button is clicked)
    elif request.method == 'POST' and 'save_button' in request.POST:
        # Debugging: print the entire POST request to check what's being sent
        print(f"POST data: {request.POST}")
        
        structured_data_json = request.POST.get('data')

        # Check if the structured_data_json is empty or None
        if structured_data_json:
            try:
                structured_data = json.loads(structured_data_json)  # Convert JSON to Python object

                # Save the structured data to the database
                for row in structured_data:
                    UserData.objects.create(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        phone=row['phone'],
                        address=row['address'],
                        city=row['city'],
                        state=row['state'],
                        country=row['country'],
                    )
                return redirect('dashboard')  # Redirect to the dashboard after saving
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return render(request, 'webapp/error.html', {'error': 'Invalid data format'})
        else:
            # If no data is found, display an error
            print("No structured data found in the POST request.")  # Debugging line
            return render(request, 'webapp/error.html', {'error': 'No data to save'})

    else:
        form = UploadDocumentForm()

    return render(request, 'webapp/upload.html', {
        'form': form,
        'structured_data': structured_data,  # Pass structured data to the template
    })


def extract_pdf_data(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or ''  # Use or '' to ensure no None values
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""  # If there’s an error, return an empty string

    return text

def role_selection_view(request):
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            request.session['role'] = role  # Save the role in session
            print(f"Role saved in session: {role}")  # Debugging line

            # Redirect based on role
            if role == 'manager':
                passcode = form.cleaned_data.get('passcode')
                if passcode == '123ABC':  # Replace with actual passcode
                    return redirect('role_based_page')  # Redirect to the dashboard
                else:
                    form.add_error('passcode', 'Invalid passcode for Manager')
            elif role == 'associate':
                return redirect('role_based_page')  # Redirect to the dashboard
    else:
        form = RoleSelectionForm()

    return render(request, 'webapp/role_select.html', {'form': form})



def role_based_page(request):
    print("role_based_page view has been invoked")  # Debugging line

    # Get the role from the session
    role = request.session.get('role', None)
    print(f"Role from session: {role}")  # Debugging line to check role retrieval

    if role == 'manager':
        can_edit = True
    elif role == 'associate':
        can_edit = False
    else:
        return redirect('role_selection')

    print(f"Can Edit Value: {can_edit}")  # Add this line to check if can_edit is set correctly

    records = UserData.objects.all()  # Replace with actual record fetching logic

    return render(request, 'webapp/dashboard.html', {
        'can_edit': can_edit,
        'records': records
    })




def manager_dashboard(request):
    # Get the role from the session
    role = request.session.get('role')

    # Check if the role is 'manager'
    is_manager = role == 'manager'

    # Fetch any records you want to display in the dashboard (if applicable)
    records = UserData.objects.all()  # Assuming Record is your model

    return render(request, 'webapp/dashboard.html', {
        'is_manager': is_manager,  # Pass whether the user is a manager
        'records': records,        # Pass any records to the template
    })


class CustomLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'webapp/login.html'
    success_url = '/role-selection/'  
    def form_valid(self, form):
        user = form.get_user()  
        
        auth_login(self.request, user)
        if not self.request.session.get('role'):
            return redirect('role_selection')  
        return redirect(self.get_success_url())