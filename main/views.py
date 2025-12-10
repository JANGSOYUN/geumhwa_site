from django.shortcuts import render

def home(request):
    return render(request, 'main/index.html')

def company(request):
    return render(request, 'main/company.html')

def products(request):
    return render(request, 'main/products.html')

def equipment(request):
    return render(request, 'main/equipment.html')

def inquiry(request):
    return render(request, 'main/inquiry.html')