from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm
from django.urls import reverse


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
    return render(request, 'rango/about.html')

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