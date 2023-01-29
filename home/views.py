import datetime

from django.contrib import messages
from django.contrib.auth import logout, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from home.forms import UserForm
from home.models import Advertisement, Category


class Home(View):
    def get(self, request):
        latest_ads = Advertisement.objects.all().order_by('id').reverse()[0:10]
        premium_ads = Advertisement.objects.filter(premium_ad=True).order_by('id').reverse()[0:10]
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
        # product_image = models.ImageField()
        import pdb;pdb.set_trace()
        title = request.POST.get('title', 'samsung s23')
        used_for = request.POST.get('used_for','1 Year')
        negotiable = request.POST.get('negotiable',False)
        category_name = request.POST.get('category', 'Electronics')
        category = Category.objects.get(name=category_name)
        state = request.POST.get('state', 'Brand New')
        description = request.POST.get('description', 'No text')
        posted_by = request.user
        posted_on = datetime.datetime.now()
        price = float(request.POST.get('price','0'))
        premium_ad = True
        warranty = request.POST.get('warranty', 'None')
        ad_obj = Advertisement.objects.create(
            title=title,
            used_for=used_for,
            negotiable=negotiable,
            category=category,
            state=state,
            description=description,
            posted_by=posted_by,
            posted_on=posted_on,
            price=price,
            premium_ad=premium_ad,
            warranty=warranty
        )
        ad_obj.save()
        import pdb;pdb.set_trace()
        return render(request=request,
                      template_name="post_ad.html",
                      context={"message": "successfully published your advertisement"}
                      )


class ShowProductDetails(View):
    def get(self, request, pk):
        item = Advertisement.objects.get(id=pk)
        return render(request=request,
                      context={'item': item},
                      template_name="product_detail.html")
