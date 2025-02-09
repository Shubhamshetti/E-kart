from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Product
from .models import Cart
import random
from .models import Address,Order
from django.db.models import Q
import re
import razorpay
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

# Create your views here.
def home(request):
    context={}
    products=Product.objects.all()
    print(products)
    context["products"]=products
    return render(request,'home.html',context)

def header(request):
    return render(request,'header.html')

def footer(request):
    return render(request,'footer.html')


def base(request):
    return render(request,'base.html')

def about(request):
    return render(request,'about.html')



def register(request):
    context={}
    if request.method=="POST":
        un=request.POST["uname"]
        em=request.POST["uemail"]
        p=request.POST["upass"]
        cp=request.POST["ucpass"]
        print(un,em,p,cp)
        if un=="" or em=="" or p=="" or cp=="":
            context["error_msg"]="All fields are required!"
            return render(request,"register.html",context)
        elif p!=cp:
                context["error_msg"]="password and confirm password are not matched!"
                return render(request,"register.html",context)
        elif len(p)<8:
            context["error_msg"]="password must be 8 characters!"
            return render(request,"register.html",context)
        else:
            u=User.objects.create(username=un,email=em,password=p)
            u.set_password(p)
            u.save()
            return redirect("/login")
    else:
        return render(request,'register.html')


def ulogout(request):
    logout(request)
    return redirect('/')
    
def contact(request):
    return render(request,'contact.html')

def ulogin(request):
    context={}
    if request.method=="POST":
        un=request.POST["uname"]
        p=request.POST["upass"]
        if un=="" or p=="":
            context["error_msg"]="All fields are required!"
            return render(request,"login.html",context)
        else:
            u=authenticate(username=un,password=p)
            print(u)
            if u!=None:
                login(request,u)
                return redirect('/')
            else:
                context["error_msg"]="Invalid User name and Password!"
                return render(request,"login.html",context)              
    else:
        return render(request,'login.html')
    
def product_details(request,pid):
    context={}
    product=Product.objects.filter(id=pid)
    context['product']=product
    return render(request,"product_details.html",context)


def filterbycategory(request,cat):
    context={}
    products=Product.objects.filter(category=int(cat))
    context['products']=products
    return render(request,"home.html",context)

def sortbyprice(request,p):
    context={}
    if p=='1':
        products=Product.objects.order_by('price').all()
        context['products']=products
        return render(request,"home.html",context)
    else:
        products=Product.objects.order_by('-price').all()
        context['products']=products
        return render(request,"home.html",context)
    
def filterbyprice(request):
    context={}
    mn=request.GET['min']
    mx=request.GET['max']
    q1=Q(price__gte=mn)
    q2=Q(price__lte=mx)
    products=Product.objects.filter(q1&q2)
    context['products']=products
    return render(request,"home.html",context)


def addtocart(request,pid):
    context={}
    product=Product.objects.filter(id=pid)
    context['product']=product
    if request.user.is_authenticated:
        u=User.objects.filter(id=request.user.id)
        p=Product.objects.filter(id=pid)
        q1=Q(userid=u[0])
        q2=Q(pid=p[0])
        cart=Cart.objects.filter(q1&q2)
        if len(cart)==1:
            context["error_msg"]="Prodcut already exist in cart!"
            return render(request,'product_details.html',context)
        else:
            cart=Cart.objects.create(userid=u[0],pid=p[0])
            context["success"]="Product added in cart successfully!"
            
            return render(request,'product_details.html',context)
    else:
        context["error_msg"]="please login first !"
        return render(request,'product_details.html',context)
        
def viewcart(request):
    carts=Cart.objects.filter(userid=request.user.id)
    context={}
    total_amount=0
    items=0
    for i in carts:
        total_amount+=i.pid.price*i.qty
        items+=i.qty
    context['total']=total_amount
    context['items']=items
    context['carts']=carts   
    return render(request,'cart.html',context)
    


def removecart(request,cid):
    cart=Cart.objects.filter(id=cid)
    cart.delete()
    return redirect('/mycart')

  
def updateqty(request,x,cid):
        cart=Cart.objects.filter(id=cid)
        quantity=cart[0].qty
        if x=='1':
            quantity+=1
        elif quantity>=1:
            quantity-=1
        cart.update(qty=quantity)
        return redirect('/mycart')

def address(request):
    context={}
    user=User.objects.filter(id=request.user.id)
    address=Address.objects.filter(user_id=user[0])
    if len(address)>=1:
        return redirect('/placeorder')
    elif request.method=="POST":
        fn=request.POST["full_name"]
        ad=request.POST["address"]
        ct=request.POST["city"]
        st=request.POST["state"]
        z=request.POST["zipcode"]
        mob=request.POST["mobile"]
        if re.match("[6-9]\d{9}",mob):
            addr=Address.objects.create(user_id=user[0],fullname=fn,address=ad,city=ct,state=st,pincode=z,mobile=mob)
            addr.save()
            return redirect('/placeorder')
        else:
            context['error_msg']="Invalid Mobile Number"
            return render(request,'address.html',context)  
    return render(request,'address.html',context) 

def placeorder(request): 
    c=Cart.objects.filter(userid=request.user.id)
    u=User.objects.filter(id=request.user.id)
    for carts in c:
        orderid=random.randint(1000,10000)
        amount=carts.pid.price*carts.qty
        order=Order.objects.create(order_id=orderid,user_id=u[0],p_id=carts.pid,qty=carts.qty,amt=amount)
        order.save()
    c.delete()
    return redirect('/fetchorder')

def fetchorder(request):
    context={}
    u=User.objects.filter(id=request.user.id)
    address=Address.objects.filter(user_id=u[0])
    q1=Q(user_id=u[0])
    q2=Q(payment_status="unpaid")
    orders=Order.objects.filter(q1&q2)
    context['address']=address
    total=0
    items=0
    for i in orders:
        total+=i.amt
        items=i.qty
    context['total']=total
    context['items']=items
    return render(request,'fetchorder.html',context)

def makepayment(request):
    u=User.objects.filter(id=request.user.id)
    q1=Q(user_id=u[0])
    q2=Q(payment_status="unpaid")
    orders=Order.objects.filter(q1&q2)
    sum=0
    for i in orders:
        sum+=i.amt
        orderid=i.order_id 
    context={}
    context['orders']=orders
    client = razorpay.Client(auth=("rzp_test_bfwC1cyirb4ypO","6l3qZkBWBwXbene26Wf8ML1L"))
    data = { "amount":sum*100, "currency" : "INR" , "receipt" : 'orderid'}
    payment=client.order.create(data=data)
    context['payment']=payment
    return render(request,'pay.html',context)


def email_send(request):
    reciver_mail=request.user.email
    send_mail(
    "Ekart-Order Confirmation",
    "Dear Customer,\n Your Order is Confirmed \n Thanks for Ordering from Ekart ",
    "shettishubham7@gmail.com",
    [reciver_mail],
    fail_silently=False,
    )
    return redirect('/update_order_status')

def update_order_status(request):
    u=User.objects.filter(id=request.user.id)
    q1=Q(user_id=u[0])
    q2=Q(payment_status="unpaid")
    orders=Order.objects.filter(q1&q2)
    orders.update(payment_status="paid")
    return redirect('/')


def send_email2(request):
    # Define the recipient, subject, and other details
    subject = "Welcome to Our Service"
    recipient_email = "shubhamshetti7@gmail.com"
    from_email = "shettishubham7@gmail.com"
    
    # Render the HTML template with context
    context = {
        'user_name': 'John Doe',
        'message_content': 'Your account has been successfully created.'
    }
    html_content = render_to_string('home.html', context)
    text_content = strip_tags(html_content)  # Fallback for email clients that don't support HTML
    
    # Create the email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[recipient_email],
    )
    email.attach_alternative(html_content, "text/html")
    
    # Send the email
    email.send()
    return redirect('/update_order_status')

