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

from . models import User, File, Field

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
        
        tempfile = NamedTemporaryFile('wt', delete=False, encoding="utf8")
        filename = f'templates/{new_file.csv_dir}'

        with open(filename, 'rt', encoding="utf8") as inp, tempfile:
            reader = csv.reader(inp)
            writer = csv.writer(tempfile)

            writer.writerow(next(reader))
            writer.writerow(next(reader))

            reader = list(csv.reader(inp))
            cat_id = reader[4][1]
        shutil.move(tempfile.name, filename)

        # fill fields
        with open(filename, 'rt', encoding="utf8") as inp:
            reader = csv.reader(inp)
            next(reader)
            reader = list(csv.reader(inp))

            for row in reader:
                for cell in row:
                    print(cell)
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

def unique(request):
    if request.method == 'POST':
        new_file = File.objects.get(id=request.POST['file_id'])
        filename = new_file.csv_dir

        tempfile = NamedTemporaryFile('wt', delete=False, encoding="utf8")

        with open(filename, 'rt', encoding="utf8") as file, tempfile:
            reader = list(csv.reader(file))
            writer = csv.writer(tempfile)

            i, j = 0
            for row in reader:
                i += 1
                writer.writerow(row)
            
            