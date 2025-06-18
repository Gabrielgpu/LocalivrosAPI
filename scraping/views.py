from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .utils.scraping import buscar_livro_por_nome
import asyncio
from books.models import Book


class ScrapingView(LoginRequiredMixin, View):
  template_name = 'home.html'
  error_message = 'Isbn é obrigatório!'
  

  def get(self, request):
    latest_books = Book.objects.order_by('-created_at')[:5]
    return render(request, self.template_name, {'books': latest_books})

  def post(self, request):
    title = request.POST.get('title')
    # metadata_database = Book.objects.filter(gtin_ean=title).first()

    if not title:
      messages.error(request, self.error_message)
      return redirect('book_search')

    metadata_scraping = self.scraping(title=title)

    request.session['book_metadata'] = metadata_scraping

    return redirect('add_book')

  def scraping(self, title=None):
    return buscar_livro_por_nome(title)