import datetime
from itertools import chain

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    search_param, num_genres_with_param, num_books_with_param = None, None, None
    if "search" in request.GET:
        search_param = request.GET["q"]
        num_genres_with_param = Genre.objects.filter(name__icontains=search_param).count()
        num_books_with_param = Book.objects.all().filter(genre__name__icontains=search_param).count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Sessions
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_with_param': num_books_with_param,
        'num_genres_with_param': num_genres_with_param,
        'q': search_param,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    pass

    @staticmethod
    def get_available_copies():
        all_books = list(Book.objects.all())
        all_instances = list(BookInstance.objects.all())
        available_books = {}

        for book in all_books:
            book_count = 0
            for copy in all_instances:
                if book.id == copy.book_id and copy.borrower_id is None:
                    book_count += 1
                    available_books[book.id] = str(book_count)
        return available_books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_copies'] = self.get_available_copies()
        context['placeholder_img'] = '../../../media/book_covers/book_placeholder.png'
        return context


class BookDetailView(generic.DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['placeholder_img'] = '../../../media/book_covers/book_placeholder.png'
        return context


class AuthorDetailView(generic.DetailView):
    model = Author
    paginate_by = 10


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['placeholder_img'] = '../../../media/book_covers/book_placeholder.png'
        return context


class AllLoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """Librarian list view"""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by(
            'due_back')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['placeholder_img'] = '../../../media/book_covers/book_placeholder.png'
        return context


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    template_name = 'catalog/forms/author_form.html'
    # def get_success_url(self):
    #     return reverse_lazy('authors')
    success_url = reverse_lazy('authors')


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__'  # Not recommended (potential security issue if more fields added)
    template_name = 'catalog/forms/author_form.html'


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'catalog/forms/author_confirm_delete.html'


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    initial = {'date_of_death': '11/06/2020'}
    template_name = 'catalog/forms/book_form.html'

    # def get_success_url(self):
    #     return reverse_lazy('authors')
    success_url = reverse_lazy('books')


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'  # Not recommended (potential security issue if more fields added)
    template_name = 'catalog/forms/book_form.html'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'catalog/forms/book_confirm_delete.html'


# class SearchListView(generic.ListView):
#     model = Book
#     paginate_by = 10
#     template_name = 'search.html'
#
#     def get_queryset(self, *args, **kwargs):
#         qs = super().get_queryset()
#         query = self.request.GET.get('search')
#         if query:
#             print('test')
#             return qs.filter(self.model.title)
#         return query
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['search_results'] = self.get_queryset()
#         return context


def search_books(request):
    # form = SearchForm(request.GET)
    # if form.is_valid():

    query = None
    if request.GET and request.GET['q']:
        query = request.GET['q']
        books = Book.objects.filter(title__icontains=query)
        authors = Author.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        search_results = list(chain(books, authors))
        results = {}
        for result in search_results:
            if isinstance(result, Book):
                if 'books' in results.keys():
                    results['books'].append(result)
                else:
                    results['books'] = []
                    results['books'].append(result)
            elif isinstance(result, Author):
                if 'authors' in results.keys():
                    results['authors'].append(result)
                else:
                    results['authors'] = []
                    results['authors'].append(result)
    if query:
        return render(request, 'catalog/search.html', {
            'query': query,
            'results': results,
            'books': books,
            'authors': authors,
            'placeholder': '../../../media/book_covers/book_placeholder.png'
            # 'form': form,
        })
    return render(request, 'catalog/search.html', {'q': None})
