from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .utils.google_books import search_books_by_title
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

    if not title:
      messages.error(request, self.error_message)
      return redirect('book_search')

    metadata_scraping = search_books_by_title(title)

    request.session['book_metadata'] = metadata_scraping

    return redirect('add_book')