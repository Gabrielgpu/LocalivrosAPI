from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.conf import settings
from .models import ApiIntegrationToken, BlingCredential
from .services.bling import create_product, increment_stock
from books.models import Book
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from requests_oauthlib import OAuth2Session
from pathlib import Path
import os


DIR = Path(__file__).resolve().parent


redirect_uri = settings.EXTERNAL_API_URI
token_url = settings.EXTERNAL_API_TOKEN_ENDPOINT
authorization_base_url = settings.EXTERNAL_API_AUTHORIZATION_END_POINT


class AuthBlingView(LoginRequiredMixin, View):

    def get(self, request):
        bling_credential = BlingCredential.objects.filter(user=request.user).first()

        if not bling_credential:
            messages.error(request, "Credenciais Bling não encontradas, registre suas credenciais!")
            return redirect('bling_credentials')
        

        client_id = bling_credential.client_id

        print(redirect_uri)

        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=["*"])
        authorization_url, state = oauth.authorization_url(authorization_base_url)

        print(oauth)

        print(authorization_url)
        print(state)

        request.session["oauth_state"] = state
        return redirect(authorization_url)


class AuthBlingCallbackView(LoginRequiredMixin, View):
    success_message = 'Token armazenado no banco de dados'

    def get(self, request):
        bling_credential = BlingCredential.objects.filter(user=request.user).first()

        if not bling_credential:
            messages.error("Credenciais Bling não encontradas, registre suas credenciais!")
            return redirect('bling_credentials')
        
        client_id = bling_credential.client_id

        client_secret = bling_credential.client_secret

        oauth = OAuth2Session(
            client_id, 
            state=request.session.get("oauth_state"), 
            redirect_uri=redirect_uri
        )

        full_url = request.build_absolute_uri()

        token = oauth.fetch_token(
            token_url,
            authorization_response=full_url,
            client_secret=client_secret
        )

        print(f"TOKEN: {token}")

        ApiIntegrationToken.objects.create(
            user=request.user,
            access_token=token.get('access_token'),
            expires_in=token.get('expires_in'),
            refresh_token=token.get('refresh_token'),

        )
        
        messages.success(
            request, 
            self.success_message
        )

        return redirect('books')



class SendProductToBlingView(LoginRequiredMixin, View):

    def post(self, request):
        id = request.POST.get('id')

        book = Book.objects.filter(id=id, user=request.user).first()

        credentials_token = ApiIntegrationToken.objects.filter(user=request.user).last()

        if credentials_token is None:
            return redirect('auth_bling')

        if not credentials_token.is_token_valid():
            token_valid = credentials_token.refresh()
            
            if not token_valid:
                messages.error(request, 'Problemas com refresh token, tente renovar suas credenciais')
                return redirect('book_search')

        product_response = create_product(book, credentials_token.access_token)
        if product_response.status_code != 201:
            messages.error(request, 'Não foi possível cadastrar livro na Bling')
            return redirect('books')
        
        book.id_bling = product_response.json()["data"]["id"]
        book.save()
        messages.success(request, 'Livro cadastrado na Bling')


        bling_credential = BlingCredential.objects.filter(user=request.user).first()

        stock_response = increment_stock(book, bling_credential.deposit_id, credentials_token.access_token)
        if stock_response.status_code != 201:
            messages.error(request, 'houve erro ao atualizar estoque.')
            return redirect('books')

        messages.success(request, 'Estoque atualizado com sucesso!')
        return redirect('books')



class CredentialsBlingToIntegrationCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = BlingCredential
    template_name = 'integration_bling.html'
    success_url = reverse_lazy('books')
    success_message = "Credencial salva!"
    fields = ["user", "client_id", "client_secret", "deposit_id"]


class EditCredentialsBlingUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = BlingCredential
    template_name = "update_credential.html"
    success_url = reverse_lazy("books")
    success_message = "Credenciais atualizadas com sucesso!"
    pk_url_kwarg = "id"
    fields = ["client_id", "client_secret", "deposit_id"]
    context_object_name = "credential"
    

    def get_queryset(self):
        return BlingCredential.objects.filter(user=self.request.user)