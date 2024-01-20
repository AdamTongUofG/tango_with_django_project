from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the index page <br> <br> <a href='/rango/about/'>About</a>" )
    #add a hyperlink for index here

def about(request):
    return HttpResponse("Rango says hey there this should be an about page! <br> <br> <a href='/rango/'>Index</a>")
