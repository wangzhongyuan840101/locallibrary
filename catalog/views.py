import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Book, Author, BookInstance, Genre


def index(request):
    """View function for home page of site"""
    num_books = Book.objects.all().count()
    # num_books_science = Book.objects.filter(genre__name__icontains='science').count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.all().count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        # 'num_books_science': num_books_science,
    }

    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user) \
            .filter(status__exact='o') \
            .order_by('due_back')


class LoanedBooksAllListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o') \
            .order_by('due_back')


from catalog.forms import RenewBookForm


@permission_required('catalog.can_mark_returned')
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

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# from catalog.forms import RenewBookModelForm
#
#
# @permission_required('catalog.can_mark_returned')
# def renew_book_librarian(request, pk):
#    book_instance = get_object_or_404(BookInstance, pk=pk)
#
#     if request.method == 'POST':
#         book_renewal_form = RenewBookModelForm(request.POST)  # RenewBookForm(request.POST)
#
#         if book_renewal_form.is_valid():
#             book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
#             book_instance.save()
#             return HttpResponseRedirect(reverse('all-borrowed'))
#     else:
#         proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
#         book_renewal_form = RenewBookModelForm(initial={'renewal_date': proposed_renewal_date})  # RenewBookForm(initial={'renewal_date': proposed_renewal_date})
#
#     context = {
#         'form': book_renewal_form,
#         'book_instance': book_instance,
#     }
#
#     return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018', }


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    # initial = {'date_of_death': '05/01/2018', }


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
