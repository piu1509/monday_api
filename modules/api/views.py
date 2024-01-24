from django.shortcuts import render, redirect
import requests
import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.views import View
from modules.api.forms import (
    ItemCreateForm, SubitemCreateForm,
    ItemUpdateForm, ItemDeleteForm)


class redirectMondayView(View):
    """
            Generates access token for an user and handles the
            authentication process of the user using the generated acces token.
    """

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        data = {
            "client_id": "726fa380a2e062c4d31b3b6c2a915ef6",
            "client_secret": "57297b74c640db8bd6e344dcfe6c88f1",
            "grant_type": "authorization_code",
            "code": str(code),
            "redirect_uri": "http://localhost:8000/api/monday_redirect/",
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(
            "https://auth.monday.com/oauth2/token", data=data, headers=headers)
        credentials = response.json()
        access_token = credentials['access_token']
        scope = credentials['scope']
        request.session['access_token'] = access_token
        apiUrl = "https://api.monday.com/v2"
        headers = {"Authorization": access_token}
        query2 = '{me { name id email location phone photo_original is_admin is_guest }}'
        data = {'query': query2}
        r = requests.post(url=apiUrl, json=data, headers=headers)
        user = r.json()
        context = {
            'user': user
        }
        context['user']
        email = context['user']['data']['me']['email']
        name = context['user']['data']['me']['name']

        user = User.objects.filter(username=email)
        if user:
            user = user[0]
        else:
            user = User.objects.create(username=email, first_name=name)
        user = login(request, user)
        return render(request, 'profile.html', context)


class Logout(LogoutView):
    """
            Handles the logout process.
    """
    template_name = 'registration/logout.html'


class ListItems(View):
    """
            Lists out all the items in monday api project.
    """
    def get(self, request, *args, **kwargs):
        if request.session.get('access_token'):
            apiKey = request.session['access_token']
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}

            query2 = '{boards (ids: 4235746662) { name id description items { name id column_values{title id type text } } } }'
            data = {'query': query2}

            r = requests.post(url=apiUrl, json=data, headers=headers)
            items = r.json()
            context = {
                "list": items
            }
            return render(request, 'api/item_list.html', context)
        else:
            return JsonResponse("You are not authenticated.", safe=False)


class CreateItem(View):
    """
            Creates a new item in board of monday api.
    """
    def get(self, request, *args, **kwargs):
        if request.session.get('access_token'):
            apiKey = request.session['access_token']
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            query3 = 'mutation{ create_item (board_id:4235746662, item_name:"Writing templates.") { id } }'
            data = {'query': query3}
            r = requests.post(url=apiUrl, json=data, headers=headers)
            return JsonResponse(r.json(), safe=False)
        else:
            return JsonResponse("Authenticate first.", safe=False)


class ItemCreate(View):
    """
            Creates new item in a board of monday api by taking user input.
    """
    form_class = ItemCreateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'api/create_item.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.session.get('access_token'):
            apiKey = request.session['access_token']
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            if form.is_valid():
                b_id = int(request.POST.get("board_id"))
                name = request.POST.get("item_name")
                status = request.POST.get("status")
                date = request.POST.get("date")
                query3 = 'mutation ($myBoardId: Int!, $myItemName: String!, $columnVals: JSON!){ create_item (board_id:$myBoardId, item_name:$myItemName, column_values:$columnVals) { id } }'
                vars = {
                    'myBoardId': b_id,
                    'myItemName': name,
                    'columnVals': json.dumps({
                        'status': {'label': status},
                        'date4': {'date': date}
                    })
                }
                data = {'query': query3, 'variables': vars}
                r = requests.post(url=apiUrl, json=data, headers=headers)
                return redirect('api:item_list')
            else:
                return render(request, 'api/create_item.html', {'form': form})
        else:
            return JsonResponse('Authenticate first.', safe=False)


class SubitemCreate(View):
    """
            Creates new subitem for an item in a board of monday api by taking user input.
    """
    form_class = SubitemCreateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'api/create_item.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.session.get('access_token'):
            apiKey = request.session['access_token']
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            if form.is_valid():
                item_id = int(request.POST.get("item_id"))
                name = request.POST.get("item_name")
                status = request.POST.get("status")
                date = request.POST.get("date")
                query = 'mutation ($parentItemId: Int!, $mySubItem: String!, $columnVals: JSON!) {create_subitem (parent_item_id: $parentItemId, item_name: $mySubItem, column_values: $columnVals) {id board { id } } }'
                vars = {
                    'parentItemId': item_id,
                    'mySubItem': name,
                    'columnVals': json.dumps({
                        'status': {'label': status},
                        'date0': {'date': date}
                    })
                }
                data = {'query': query, 'variables': vars}
                r = requests.post(url=apiUrl, json=data, headers=headers)
                return JsonResponse(r.json(), safe=False)
            else:
                return render(request, 'api/create_item.html', {'form': form})
        else:
            return JsonResponse('Authenticate first.', safe=False)


class ItemUpdate(View):
    """
            Updates multiple column values of an item in monday api.
    """
    form_class = ItemUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'api/create_item.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.session.get('access_token'):
            apiKey = request.session['access_token']
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            if form.is_valid():
                board_id = int(request.POST.get('board_id'))
                item_id = int(request.POST.get('item_id'))
                name = request.POST.get('item_name')
                status = request.POST.get('status')
                date = request.POST.get('date')
                query = 'mutation ($board_id: Int!, $item_id: Int!, $column_values: JSON!){ change_multiple_column_values(board_id:$board_id, item_id:$item_id, column_values:$column_values) { id } }'
                vars = {
                    'board_id': board_id,
                    'item_id': item_id,
                    'column_values': json.dumps({
                        'name': name,
                        'status': {'label': status},
                        'date4': {'date': date}
                    })
                }
                data = {'query': query, 'variables': vars}
                r = requests.post(url=apiUrl, json=data, headers=headers)
                return redirect('api:item_list')
            else:
                return render(request, 'api/create_item.html', {'form': form})
        else:
            return JsonResponse("Authenticate first.", safe=False)


class ItemDelete(View):
    """
            Deletes an item with given id from a board in monday api.
    """
    form_class = ItemDeleteForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'api/create_item.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.session.get('access_token'):
            apiKey = request.session['access_token']
            apiUrl = "https://api.monday.com/v2"
            headers = {"Authorization": apiKey}
            if form.is_valid():
                item_id = int(request.POST.get('item_id'))
                query = 'mutation ($item_id: Int!){delete_item(item_id: $item_id) {id name state}}'
                vars = {'item_id': item_id}
                data = {'query': query, 'variables': vars}
                r = requests.post(url=apiUrl, json=data, headers=headers)
                return redirect('api:item_list')
            else:
                return render(request, 'api/create_item.html', {'form': form})
        else:
            return JsonResponse("Authenticate first.", safe=False)
