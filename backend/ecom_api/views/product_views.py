from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser


from ..models.product import Product, Review
from ..serializers import ProductSerializer

# Create your views here.
                           
    
#     '/api/products          <== GET Request',                  
    
#     '/api/products/<id>     <== GET Request',

#     '/api/products          <== POST Request',

#     '/api/products/<id>     <== PUT Request',

#     '/api/products/<id>     <== Delete Request',      



@api_view(['GET'])
def getProducts(request):

    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data) 




@api_view(['GET'])
def getProduct(request, pk):

    if request.method == 'GET':
        product = Product.objects.get(_id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)



