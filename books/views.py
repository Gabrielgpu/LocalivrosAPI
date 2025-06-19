from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy   
from django.shortcuts import redirect
from django.db.models import Q
from .models import Book
from .forms import EditBookForm




class BookCreateView(LoginRequiredMixin, CreateView):
  template_name = 'register_book.html'
  success_url = reverse_lazy('book_search')
  success_message = 'livros foram cadastrados'
  error_message = 'Dados insuficientes para cadastrar o livro.'
  

  def get(self, request, *args, **kwargs):
    metadata = request.session.get('book_metadata')
    return render(request, self.template_name, {'metadata': metadata})

  def post(self, request, *args, **kwargs):
    metadata = request.session.pop('book_metadata', None)
    # stock = request.POST.get('stock')

    books_id = request.POST.getlist("books")

    if books_id:
      for id in books_id:
        id = int(id)
        book = Book.objects.create(
          user = request.user,
          description = metadata[id].get('title', ''),
          gtin_ean = metadata[id].get('gtin_ean', ''),
          mark = metadata[id].get('editora', ''),
          short_description = metadata[id].get('short_description', ''),
          url_external_images = metadata[id].get('url_external_images', ''),
          product_category = metadata[id].get('product_category', ''),
          year_published = metadata[id].get('year_published', ''),
          page_of_number = metadata[id].get('page_of_number', ''),
          author = metadata[id].get('author', ''),
          stock = 1
        )
        
        book.code = f"LC-{book.id}"
        book.save()
        
    else:
      messages.error(request, self.error_message)
      return redirect('book_search')

    messages.success(request, f"{len(books_id)} - {self.success_message}")
    return redirect(self.success_url)

class BookListView(LoginRequiredMixin, ListView):
  model = Book
  template_name = 'books.html'
  context_object_name = 'products'
  paginate_by = 10
  ordering = ['id']

  def get_queryset(self):
      queryset = self.model.objects.filter(user=self.request.user)

      query = self.request.GET.get('query')

      if query:
        search_fields = ['id', 'created_at', 'description', 'gtin_ean', 'product_category', 'author', 'user_id__username', 'year_published']

        query_objects = Q()
        for field in search_fields:
          query_objects |= Q(**{f"{field}__icontains": query})

        queryset = queryset.filter(query_objects)

      return queryset
  

class BookDetailView(LoginRequiredMixin, DetailView):
  model = Book
  template_name = 'detail_book.html'
  pk_url_kwarg = 'id'
  context_object_name = 'product'

class BookUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
  form_class = EditBookForm
  model = Book
  pk_url_kwarg = 'id'
  template_name = 'update_book.html'
  success_url = reverse_lazy('books')
  success_message = 'Livro atualizado!'

class BookDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
  pk_url_kwarg = 'id'
  model = Book
  success_url = reverse_lazy('books')
  success_message = 'Livro removido!'

  



