import datetime

from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from home.forms import UserForm
from home.models import Advertisement, Category, Comments, Replies, UserRating


class Home(View):
    def get(self, request):
        latest_ads = Advertisement.objects.all().order_by('id').reverse()[0:8]
        premium_ads = Advertisement.objects.filter(premium_ad=True).order_by('id').reverse()[0:2]
        categories = Category.objects.all()
        return render(request,
                      context={'latest_ads': latest_ads,
                               'premium_ads': premium_ads,
                               'categories': categories},
                      template_name='home.html')


class Registration(View):
    def get(self, request):
        form = UserForm()
        return render(request=request,
                      template_name="registration/signup.html",
                      context={"register_form": form})

    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Successfully registered")
            return redirect("login")
        messages.error(request, "Registration failed. Please try again!")
        return render(request=request,
                      template_name="registration/signup.html",
                      context={"form": form})


class SignOutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login')


@method_decorator(csrf_exempt, name='dispatch')
class PostAdvertisement(View):
    def get(self, request):
        return render(request=request,
                      template_name="post_ad.html"
                      )

    def post(self, request):
        title = request.POST.get('title', 'samsung s23')
        used_for = request.POST.get('used_for', '1 Year')
        negotiable = request.POST.get('negotiable', False)
        category_name = request.POST.get('category', 'Electronics')
        category = Category.objects.get(name=category_name)
        state = request.POST.get('state', 'Brand New')
        description = request.POST.get('description', 'No text')
        posted_by = User.objects.get(id=1)  # request.user
        posted_on = datetime.datetime.now()
        product_image = request.FILES['file']
        price = float(request.POST.get('price', '0'))
        premium_ad = True
        warranty = request.POST.get('warranty', 'None')
        ad_obj = Advertisement.objects.create(title=title, used_for=used_for, negotiable=negotiable,
                                              category=category, state=state, description=description,
                                              posted_by=posted_by, posted_on=posted_on, price=price,
                                              premium_ad=premium_ad, warranty=warranty, product_image=product_image
                                              )
        category.total_ads += 1
        ad_obj.save()
        category.save()
        return render(request=request,
                      template_name="post_ad.html",
                      context={"message": "successfully published your advertisement"}
                      )


@method_decorator(csrf_exempt, name='dispatch')
class PostComment(View):
    def post(self, request, pk):
        advertisement_obj = Advertisement.objects.get(id=pk)
        comment = request.POST.get('comment')
        comment_obj = Comments(
            product=advertisement_obj,
            description=comment,
            posted_on=datetime.datetime.now(),
            posted_by=request.user
        )
        comment_obj.save()
        return redirect('product_details', pk=f'{advertisement_obj.id}')


class PostRelies(View):
    def post(self, request, comment_id):
        comment = Comments.objects.get(id=comment_id)
        reply = Replies(
            comment=comment,
            posted_by=request.user,
            description=request.POST.get('reply'),
            posted_on=datetime.datetime.now()
        )
        return redirect('product_details')


class GetProductList(View):
    def get(self, request, category_id, page=1):
        category = Category.objects.get(id=category_id)
        products = Advertisement.objects.filter(category=category).order_by("views")
        paginator = Paginator(products, per_page=5)
        paginated_products = paginator.get_page(page)
        return render(request=request,
                      context={'category_id': category.id,
                               'category_title': category.name,
                               'products': paginated_products.object_list,
                               'page_obj': paginated_products,
                               },
                      template_name="product_list.html")


class ShowProductDetails(View):
    def get(self, request, pk):
        comment_to_replies = []
        item = Advertisement.objects.get(id=pk)

        Advertisement.objects.filter(id=pk).update(views=item.views + 1)
        if request.user.is_authenticated:
            user_rating = UserRating.objects.filter(
                Q(advertisement=item) & Q(user=request.user)).first()

            if user_rating:
                user_rating.num_of_clicks += 1
                user_rating.save()
            else:
                user_rating = UserRating(
                    advertisement=item,
                    user=request.user,
                    num_of_clicks=1,
                )
                user_rating.save()
        comments = Comments.objects.filter(product=item).order_by('id')

        for comment in comments:
            replies = Replies.objects.filter(comment=comment).order_by('id')
            comment_to_replies.append({comment: replies})
        return render(request=request,
                      context={'item': item, 'comments': comment_to_replies},
                      template_name="product_detail.html")


@method_decorator(csrf_exempt, name='dispatch')
class SearchProduct(View):
    def get(self, request, page=1):
        query = request.GET.get('q')
        products = Advertisement.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        paginator = Paginator(products, per_page=8)
        paginated_products = paginator.get_page(page)
        return render(request=request,
                      context={
                          'products': paginated_products.object_list,
                          'page_obj': paginated_products,
                      },
                      template_name="search_list.html")


@method_decorator(login_required, name='dispatch')
class Dashboard(View):
    def get(self, request):
        ad_type = 'all'
        user = User.objects.get(id=request.user.id)
        ads_posted = Advertisement.objects.filter(posted_by=user)
        if ad_type == 'sold':
            ads = ads_posted.filter(sold=True).all()
        elif ad_type == 'live':
            ads = ads_posted.filter(sold=False).all()
        else:
            ads = ads_posted.all()
        return render(
            request=request,
            context={
                'ads': ads
            },
            template_name='dashboard.html'
        )


class GetRecommendations(View):
    def get(self, request, pk):
        return HttpResponseRedirect('login')
