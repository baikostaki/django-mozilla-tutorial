from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.views import generic

from .models import Book, Author, BookInstance, Genre


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    search_param, num_genres_with_param, num_books_with_param = None, None, None
    if "search" in request.GET:
        search_param = request.GET["search"]
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
        'search_param': search_param,
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
        return context


class BookDetailView(generic.DetailView):
    model = Book


class AuthorDetailView(generic.DetailView):
    model = Author
    paginate_by = 2


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """Librarian list view"""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by(
            'due_back')
