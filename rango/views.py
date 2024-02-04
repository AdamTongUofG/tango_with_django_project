from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    # Render the response and send it back!
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #prints out whether the method is a GET or a POST
    print(request.method)
    #prints out the user name, if no one is logged in it prints "AnonymousUser"
    print(request.user)
    return render(request, 'rango/about.html', {})

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        #The .get() method returns one model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)
        #retrieves all of the associiated pages
        pages = Page.objects.filter(category=category)

        #adds our results list to the template context under name pages
        context_dict['pages'] = pages
        #we also add the category object from the databasse to the context dictionary
        context_dict['category'] = category

    except Category.DoesNotExist:
        #it only reaches here if we can't find the specified category
        #the template will display the "no category" message for us
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    #HTTP Post
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #check if form is valid
        if form.is_valid():
            #save the new category to the database
            form.save(commit=True)
            #redirect the user back to the index view
            return redirect(reverse("{% url 'rango:index' %}"))
        else:
            #if the form contains errors
            print(form.errors)

    #will handle the form in all cases
    #or will render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    #you cannot add a page to a category that does not exist
    if category is None:
        return redirect(reverse("{% url 'rango:index' %}"))
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse("{% url 'rango:add_page' category.slug %}"))
            
        else:
            print(form.errors)

    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', context={'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')
    

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))