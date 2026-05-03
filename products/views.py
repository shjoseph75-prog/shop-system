from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Sale
from .forms import ProductForm, SaleForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count



@login_required
def home(request):
    form = ProductForm()

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        
    products = Product.objects.all()
    low_stock = Product.objects.filter(quantity__lt=10)

    total_products = Product.objects.count()
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    return render(request, 'products/home.html', {
        "products": products,
        "form": form,
        "low_stock": low_stock,
        "total_products": total_products,
        "total_sales": total_sales,
        "total_revenue": total_revenue

    })

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect("/")

def edit_product(request, id):
    product =  get_object_or_404(Product, id = id)

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")

        if name and price and quantity:
            product.name = name
            product.price = price
            product.quantity = quantity
            product.save()
            return redirect("/")
        
    return render (request, 'products/edit.html', {"product": product})
   

def sell_product(request):
    form = SaleForm()

    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)

            product = sale.product


            if sale.quantity_sold > product.quantity:
                return render(request, 'products/sell.html', {
                    "form": form,
                    "error": "not enough stock!"\
                    
                })
            product.quantity -= sale.quantity_sold
            product.save()

            sale.total_price = sale.quantity_sold * product.price
            sale.save()

            return redirect("/")

    return render(request, 'products/sell.html', {"form": form})    


@login_required
def sales_history(request):
    sales = Sale.objects.all().order_by('-date')
    total_revenue = Sale.objects.aggregate(Sum('total_price'))['total_price__sum']

    return render(request, 'products/sales.html', {
        "sales": sales,
        "total_revenue": total_revenue
    })




