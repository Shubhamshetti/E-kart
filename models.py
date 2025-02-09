from django.db import models

#Create your models here.
class Product(models.Model):
    CAT=((1,"shoes"),(2,"mobile"),(3,"cloths"),(4,"watch"))
    pname=models.CharField(max_length=50,verbose_name="Product Name")
    price=models.FloatField()
    category=models.IntegerField(choices=CAT ,verbose_name="Category")
    description=models.CharField(max_length=300 , verbose_name="Details")
    is_active=models.BooleanField(default=True, verbose_name="Is_Available")
    pimage=models.ImageField(upload_to='image')
    def __str__(self):
        return self.pname
    
class Cart(models.Model):
    userid=models.ForeignKey("auth.user", on_delete=models.CASCADE,db_column='userid')
    pid=models.ForeignKey("Product", on_delete=models.CASCADE,db_column='pid')
    qty=models.IntegerField(default=1)


class Address(models.Model):
    user_id=models.ForeignKey("auth.User",on_delete=models.CASCADE, db_column="user_id")
    address=models.CharField(max_length=200)
    fullname=models.CharField(max_length=40)
    city=models.CharField(max_length=30)
    pincode=models.CharField(max_length=10)
    state=models.CharField(max_length=30)
    mobile=models.CharField(max_length=10)
    
class Order(models.Model):
    order_id=models.CharField(max_length=50)
    user_id=models.ForeignKey("auth.User",on_delete=models.CASCADE, db_column="user_id")
    p_id=models.ForeignKey("Product",on_delete=models.CASCADE,db_column="p_id")
    qty=models.IntegerField(default=1)
    amt=models.FloatField()
    payment_status=models.CharField(max_length=30,default="unpaid")