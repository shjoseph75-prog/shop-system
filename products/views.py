from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Sale, Category
from .forms import ProductForm, SaleForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone



@login_required
def home(request):
    form = ProductForm()

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/")
        
    search = request.GET.get('search')

    if search:
        products = Product.objects.filter(name__icontains=search)
    else:
        products = Product.objects.all()

    category_id = request.GET.get('category')

    if category_id:
        products = products.filter(category_id=category_id)


    total_products = Product.objects.count()

    low_stock_count = Product.objects.filter(quantity__lt=10).count()

    total_stock_value = Product.objects.aggregate(total=Sum('price'))['total'] or 0
    
    categories = Category.objects.all()

    return render(request, 'products/home.html', {
        "products": products,
        "form": form,
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "total_stock_value": total_stock_value,
        "categories": categories

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

    today = timezone.now().date()
    today_revenue = Sale.objects.filter(date__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0
    top_products = Sale.objects.values('product__name').annotate(total_sold=Sum('quantity_sold')).order_by('-total_sold')[:5]
    total_profit = Sale.objects.aggregate(
        profit=Sum(
            (F('product__price') - F('product__cost_price')) * F('quantity_sold')
        )
    )['profit'] or 0

    return render(request, 'products/sales.html', {
        "sales": sales,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "top_products": top_products,
        "total_profit": total_profit

    })






