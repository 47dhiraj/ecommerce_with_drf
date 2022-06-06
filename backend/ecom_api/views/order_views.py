import os
from django.shortcuts import render, redirect
import requests            

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from ecom_api.models import Product, Order, OrderItem, ShippingAddress
from ecom_api.serializers import ProductSerializer, OrderSerializer

from rest_framework import status

from decimal import Decimal
from datetime import datetime
from django.conf import settings

from ecom_api.utils import EmailThread
from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string, get_template
from io import BytesIO
from xhtml2pdf import pisa




@api_view(['POST'])
@permission_classes([IsAuthenticated])         
def addOrderItems(request):

    user = request.user                         
    data = request.data                         

    orderItems = data['orderItems']      

    if not data['paymentMethod']:
        return Response({'detail': 'Payment method is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not all([data['shippingAddress']['address'], data['shippingAddress']['city'], data['shippingAddress']['country']]):
        return Response({'detail': 'Detail shippingAddress info is required'}, status=status.HTTP_400_BAD_REQUEST)   

    if not orderItems and len(orderItems) == 0:    
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
    
    backend_product_price = Decimal('0.00')
    for i in orderItems:
        product = Product.objects.get(_id = i['product'])
        backend_product_price += product.price * i['qty']

    frontend_product_price = Decimal(data['totalPrice']) - (Decimal(data['shippingPrice']) + Decimal(data['taxPrice']))
    print('Backend Product Price : ', backend_product_price)
    print('Frontend Product Price : ', frontend_product_price)

    if backend_product_price != frontend_product_price:
        return Response({'detail': 'Invalid product price on the cart'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:

        order = Order.objects.create(
            user = user,
            paymentMethod = data['paymentMethod'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            totalPrice = data['totalPrice']
        )


        shipping = ShippingAddress.objects.create(
            order = order,                                 
            address = data['shippingAddress']['address'],
            city = data['shippingAddress']['city'],
            postalCode = data['shippingAddress']['postalCode'],
            country = data['shippingAddress']['country'],
        )

        for i in orderItems:
            product = Product.objects.get(_id = i['product'])       

            
            item = OrderItem.objects.create(
                product = product,                                
                order = order,                                    
                name = product.name,                                
                qty = i['qty'],
                price = i['price'],
                image = product.image.url,
            )

            # (4) Updating stock quantity
            product.countInStock -= item.qty                        
            product.save()                     


        serializer = OrderSerializer(order, many=False)            
        return Response(serializer.data)                         



@api_view(['GET'])
@permission_classes([IsAuthenticated])                             
def getOrderById(request, pk):

    user = request.user

    try:
        order = Order.objects.get(_id = pk)

        if user.is_staff or order.user == user:                     

            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)

        else:
            Response({'detail': 'Unauthorized user cannot view the order.'}, status=status.HTTP_400_BAD_REQUEST)
    
    except:
        return Response({'detail': 'Order does not exists.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):

    user = request.user
    orders = user.order_set.all()               

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)






def email_pdf(order_id, refId):
    try:
        order = get_object_or_404(Order, _id=order_id, isPaid=True)
    except:
        return Response({'detail': 'Not Found'}, status=status.HTTP_400_BAD_REQUEST)
    
    template = get_template('ecom_api/invoice.html')

    data = {
        'order': order,
        'username': order.user.username,
        'email': order.user.email,
        'paymentMethod': order.paymentMethod,
        'taxPrice': order.taxPrice,
        'shippingPrice': order.shippingPrice,
        'totalPrice': order.totalPrice,
        'paidAt': order.paidAt,
        'refId': refId
    }

    html  = template.render(data)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), response)
    pdf = response.getvalue()
    filename = 'Payment_Invoice' + '.pdf'

   
    mail_subject = 'Payment of Order'
    context_dict = {
        'user': order.user,
        'order': order
    }
    template = get_template('ecom_api/email_invoice.html')
    message  = template.render(context_dict)
    to_email = order.user.email

    
    email = EmailMultiAlternatives(
        mail_subject,
        message,                            
        settings.EMAIL_HOST_USER,
        [to_email]
    )

    if email:
        email.attach_alternative(message, "text/html")
        email.attach(filename, pdf, 'application/pdf')
        EmailThread(email).start()
    
    return True



@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny, ])
def esewaPayment(request):

    oid = request.GET.get("oid")                        
    amt = Decimal(request.GET.get("amt"))               
    refId = request.GET.get("refId")                   

    if not all([oid, amt, refId]):
        return Response({'detail': 'Unauthorized Payment'}, status=status.HTTP_400_BAD_REQUEST)           

    try:
        import xml.etree.ElementTree as ET                 

        order = Order.objects.get(_id=oid)

        if order.isPaid == True:
            return Response({'detail': 'Unauthorized Payment'}, status=status.HTTP_400_BAD_REQUEST)

        if order.totalPrice != amt:
            return Response({'detail': 'Invalid Amount'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        url = "https://uat.esewa.com.np/epay/transrec"      

        d = {                                              
            'amt': amt,
            # 'tAmt': amt,
            'scd': 'EPAYTEST',
            'rid': refId,
            'pid': oid,
        }

        resp = requests.post(url, d)           
        root = ET.fromstring(resp.content)     
        verify_status = root[0].text.strip()   

        if verify_status == "Success":
            order.isPaid = True
            order.paidAt = datetime.now()
            order.save()

            if order.isPaid==True:
                email_pdf(order._id, refId)
                return redirect("http://127.0.0.1:3000/order/"+oid)
                # return Response({'detail': 'Payment Completed and Invoice Sent'}, status=status.HTTP_200_OK)
            return Response({'detail': 'Payment Completed but Invoice not sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Payment unsuccessful'}, status=status.HTTP_400_BAD_REQUEST)

    except:
        return Response({'detail': 'Unauthorized Payment'}, status=status.HTTP_400_BAD_REQUEST)




