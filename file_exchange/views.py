import os
from unicodedata import name
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import csv
from tempfile import NamedTemporaryFile
import shutil
import json
from datetime import datetime

from . models import ListingInfo, SavedTemplate, User, File, Field

# Create your views here.

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "file_exchange/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "file_exchange/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "file_exchange/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "file_exchange/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "file_exchange/register.html")

@csrf_exempt
def index(request):
    if request.method == 'GET':
        return render(request, "file_exchange/index.html")
    else:
        file = request.FILES['csv-file']
        new_file = File(csv_dir=file.name)
        new_file.save()


        # delete uneccessary file data
        with open(f'templates/{new_file.csv_dir}', 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # tempfile = NamedTemporaryFile('wt', delete=False, encoding="utf8")
        filename = f'templates/{new_file.csv_dir}'

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

        with open(filename, 'rt', encoding="utf8", newline='') as inp:
            filename = 'templates/ebay-listings-' + str(dt_string) + '.csv'
            with open(filename, 'wt', encoding="utf8") as out:
                reader = csv.reader(inp)
                writer = csv.writer(out)

                next(reader)
                writer.writerow(next(reader))

                reader = list(csv.reader(inp))
                cat_id = reader[4][1]
        # shutil.move(tempfile.name, filename)

        new_file.csv_dir = filename
        # fill fields
        with open(filename, 'rt', encoding="utf8", newline='') as inp:
            reader = csv.reader(inp)
            reader = list(csv.reader(inp))

            for row in reader:
                for cell in row:
                    # print(cell)
                    field = Field()
                    field.name = cell
                    field.save()
                    new_file.headers.add(field)
                    new_file.save()
                    
        res = [int(i) for i in cat_id.split() if i.isdigit()]


        return render(request, "file_exchange/static_fields.html", {
            "headers": new_file.headers.all(),
            "cat_id": res[0],
            "file_id": new_file.id
        })

# def unique(request):
#     if request.method == 'POST':
#         new_file = File.objects.get(id=request.POST['file_id'])
#         filename = new_file.csv_dir

#         tempfile = NamedTemporaryFile('wt', delete=False, encoding="utf8")

#         with open(filename, 'rt', encoding="utf8") as file, tempfile:
#             reader = list(csv.reader(file))
#             writer = csv.writer(tempfile)

#             i, j = 0
#             for row in reader:
#                 i += 1
#                 writer.writerow(row)

@csrf_exempt
def static(request):
    new_file = File.objects.get(id=request.POST['file_id'])

    # inputs = [value for name, value in request.POST.iteritems() if name.startswith('v_')]

    inputs = request.POST.keys()

    for input in inputs:
        if input == 'save':
            continue
        field = Field(name=input, value=request.POST[input])
        field.save()
        new_file.static.add(field)
        new_file.save()
    
    if request.user.is_authenticated:
        if request.POST['save'] != 'False':
            template = SavedTemplate.objects.create(user=request.user, name=request.POST['save'], file=new_file)
    
    return render(request, "file_exchange/unique.html", {
        "inputs": new_file.static.all()
    })

@csrf_exempt
def unique(request):
    if request.method == 'POST':

        new_file = File.objects.get(id=request.POST['file_id'])

        new_listing = ListingInfo()
        new_listing.save()

        inputs = request.POST.keys()

        for input in inputs:
            if input == 'end' or input == 'file_id':
                continue
            field = Field(name=input, value=request.POST[input])
            field.save()
            # print(f"{field.name}: {field.value}")
            new_listing.data.add(field)
            new_listing.save()
        
        new_file.listings.add(new_listing)
        new_file.save()

        if 'end' in request.POST:
            filename = f"templates/{new_file.csv_dir}"
            tempfile = NamedTemporaryFile('wt', delete=False, encoding="utf8", newline='')

            with open(filename, 'rt', encoding="utf8", newline='') as file, tempfile:
                writer = csv.writer(tempfile)
                reader = csv.reader(file)
                writer.writerow(next(reader))

                for listing in new_file.listings.all():
                    row = []
                    for data in listing.data.all():
                        row.append(data.value)
                    writer.writerow(row)

            shutil.move(tempfile.name, filename)

            return render(request, 'file_exchange/download.html', {
                "file": filename,
                "id": new_file.id
            })

        else:
            return render(request, "file_exchange/unique.html", {
                "inputs": new_file.static.all()
            })

def download(request, id):

    file = File.objects.get(id=id)
    filename = file.csv_dir

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # with open(os.path.join(base_dir+'/',filename), 'wt') as f:
    #     for data in filename:
    #         f.write(data)
    #     f.close()
    
    with open(os.path.join(base_dir+'/templates',filename), 'rt', newline='') as f:
        data = f.read()

    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename="listings.csv"'
    return response

def templates(request):
    if request.user.id is None:
        return HttpResponseRedirect(reverse('login'))

    return render(request, "file_exchange/templates.html", {
        "templates": SavedTemplate.objects.filter(user=request.user).all
    })

def template(request, id):
    template = SavedTemplate.objects.get(id=id)
    new_file = template.file

    # field = Field(name='skip', value='skip')
    # field.save()
    # new_file.static.add(field)
    # new_file.save()

    return render(request, "file_exchange/template.html", {
        "inputs": new_file.static.all()
    })