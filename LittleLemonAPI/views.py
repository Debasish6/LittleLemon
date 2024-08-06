from django.shortcuts import render,get_object_or_404
from .models import MenuItem,Category,Cart,Order,OrderItem,Booking
from .serializers import MenuItemSerializer,CategorySerializer, UserSerializer, CartSerializer, OrderSerializer,OrderDetailSerializer
from rest_framework import generics,status
from django.contrib.auth.models import User,Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter,OrderingFilter
from datetime import date,datetime
from django.core.paginator import Paginator,EmptyPage
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .throttle import PerMinuteThrottle
from rest_framework.decorators import permission_classes,throttle_classes
from .forms import BookingForm
import json
from django.core import serializers

# Create your views here.

def index(request):
    return render(request, 'index1.html',{})

def about(request):
    return render(request, "about.html")

def menu(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'menu.html', {"menu": menu_items,"data" : [1, 2, 3]})

def book(request):
    form = BookingForm
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'book.html', context)

def bookings(request):
    if request.method == 'POST':
        data = json.load(request)
        exist = Booking.objects.filter(booking_date=data['booking_date']).filter(
            no_of_guests=data['no_of_guests']).exists()
        if exist==False:
            booking = Booking(
                name=data['name'],
                booking_date=data['booking_date'],
                no_of_guests=data['no_of_guests'],
            )
            booking.save()
        else:
            return Response("{'error':1}", content_type='application/json')
    
    date = request.GET.get('date',datetime.today().date())

    bookings = Booking.objects.all().filter(booking_date=date)
    booking_json = serializers.serialize('json', bookings)

    return Response(booking_json, content_type='application/json')

#Show all Menu
@throttle_classes([AnonRateThrottle, UserRateThrottle])
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ['title', 'price', 'category__title']
    ordering_fields = ['title', 'price', 'category__title']
    search_fields = ['title']
    
    def get(self, request):
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('price')
        search = request.query_params.get('search')
        
        if category_name:
            self.queryset = self.queryset.filter(category__title = category_name)
        if to_price:
            self.queryset = self.queryset.filter(price = to_price)
        if search:
            self.queryset = self.queryset.filter(title__contains = search)
        return super().get(request)
    
    def post(self, request):
        if request.user.groups.filter(name = 'Manager').exists() or request.user.is_superuser:
            return super().post(request)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)
    
    def put(self, request):
        if request.user.groups.filter(name = 'Manager').exists():
            return super().post(request)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)

    def patch(self, request):
        if request.user.groups.filter(name = 'Manager').exists():
            return super().post(request)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)

    def delete(self, request):
        if request.user.groups.filter(name = 'Manager').exists():
            return super().post(request)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)
    


#Show only one Menu
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        if request.user.groups.filter(name = 'Manager').exists():
            return super().put(request, *args, **kwargs)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)
    
    def patch(self, request, *args, **kwargs):
        if request.user.groups.filter(name = 'Manager').exists():
            return super().patch(request, *args, **kwargs)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if request.user.groups.filter(name = 'Manager').exists():
            return super().delete(request, *args, **kwargs)
        return Response({"message": "You are not authorized"}, status = status.HTTP_403_FORBIDDEN)

#Category View
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def post(self, request):
        if request.user.is_authenticated:
            if request.user.groups.filter(name = "Manager").exists() or request.user.is_superuser:
                return super().post(request)
            else:
                return Response({'message': 'You are not authorized'},status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'You are not authenticated'},status.HTTP_401_UNAUTHORIZED)
        
#Show all Manager
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class ManagersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class= UserSerializer
    
    def get(self,request):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().get(request)
        else:
            return Response({'message':'You are not authorized'}, status.HTTP_403_FORBIDDEN)
    
    def post(self,request):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name='Manager')
                managers.user_set.add(user)
                return Response({'message':'New Manager created succssesfully.'},  status.HTTP_201_CREATED)
            else:
                return Response({'message':'User name Required'},  status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'You are not authorized'}, status.HTTP_403_FORBIDDEN)

#Remove Manager 
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class RemoveManager(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class= UserSerializer
    
    def delete(self,request,*args,**kwargs):
        if request.user.groups.filter(name = 'Manager').exists():
            user= self.get_object()
            managers = Group.objects.get(name='Manager')
            if user in managers.user_set.all():
                managers.user_set.remove(user)
                return Response({'message':'User Removed from manager list.'}, status.HTTP_200_OK)
            else:
                return Response({'message':'User not found'}, status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':'You are not authorized'}, status.HTTP_403_FORBIDDEN)

#Show all delivary crew
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class DeliveryCrewView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer
    
    def get(self,request):
        if request.user.groups.filter(name='Manager').exists():
            return super().get(request)
        else:
            return Response({'message':'You are not authorized'},status.HTTP_403_FORBIDDEN)
    
    def post(self,request):
        if request.user.groups.filter(name='Manager').exists():
            username = request.data['username']
            if username:
                user = get_object_or_404(User,username=username)
                Delivery_crew = Group.objects.get(name='Delivery crew')
                Delivery_crew.user_set.add(user)
                return Response({'message':'Delivary Crew created Successfully.'}, status.HTTP_201_CREATED)
            else:
                return Response({'message':'User name Required'},  status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'You are not authorized'}, status.HTTP_403_FORBIDDEN)

#Remove delivary crew  
@throttle_classes([PerMinuteThrottle, UserRateThrottle])       
class RemoveDeliveryCrew(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class= UserSerializer
    
    def delete(self,request,*args,**kwargs):
        if request.user.groups.filter(name = 'Manager').exists():
            user= self.get_object()
            delivery_crews = Group.objects.get(name='Delivery crew')
            if user in delivery_crews.user_set.all():
                delivery_crews.user_set.remove(user)
                return Response({'message':'User Removed from Delivary crew list.'}, status.HTTP_200_OK)
            else:
                return Response({'message':'User not found'}, status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':'You are not authorized'}, status.HTTP_403_FORBIDDEN)
        
#Cart Items Views
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class Cart_items_views(generics.ListCreateAPIView,generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get(self,request):
        if request.user.is_authenticated:
            if not request.user.groups.filter(name__in = ['Manager','Delivery crew']).exists():
                cart_items = self.queryset.filter(user = request.user)
                serializer = self.serializer_class(cart_items,many=True)
                return Response(serializer.data,status.HTTP_200_OK)
            else:
                return Response({'message':'You are not authorized'}, status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message':'You are not authenticated'}, status.HTTP_401_UNAUTHORIZED)
        
    def post(self,request,*args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.groups.filter(name__in = ['Manager','Delivery crew']).exists():
                serializer = self.serializer_class(data = request.data,context = {'request': request})
                if serializer.is_valid():
                    serializer.save(user = request.user)
                    return Response(serializer.data, status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'You are not authorised'}, status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message':'You are not authenticated'}, status.HTTP_401_UNAUTHORIZED)
    
    def delete(self,request,*args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.groups.filter(name__in = ['Manager','Delivery crew']).exists():
                cart_items = self.queryset.filter(user = request.user)
                cart_items.delete()
                return Response({'messege':'Cart item deleted succesfully.'}, status.HTTP_200_OK)
            else:
                return Response({'message':'You are not authorised'}, status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message':'You are not authenticated'}, status.HTTP_401_UNAUTHORIZED)

#Show orders for customer, delivery crew and manager
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'delivery_crew__username', 'status', 'total', 'date']
    ordering_fields = ['user__username', 'delivery_crew__username', 'status', 'total', 'date']
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.query_params.get('user')
            delivery_crew = request.query_params.get('delivery_crew')
            date = request.query_params.get('date')
            total = request.query_params.get('total')
            
            if user:
                self.queryset = self.queryset.filter(user__username = user)
            if delivery_crew:
                self.queryset = self.queryset.filter(delivery_crew__username = delivery_crew)
            if date:
                self.queryset = self.queryset.filter(date = date)
            if total:
                self.queryset = self.queryset.filter(total = total)
            
            if request.user.groups.filter(name = 'Manager').exists():
                orders = self.queryset.all()
                all_orders = self.filter_queryset(orders)
                serializer =  self.serializer_class(all_orders,many=True)
                return Response(serializer.data, status.HTTP_200_OK)
            
            elif request.user.groups.filter(name = 'Delivery crew').exists():
                orders = self.queryset.filter(delivery_crew = request.user)
                delivery_crew_orders = self.filter_queryset(orders)
                serializer = self.serializer_class(delivery_crew_orders,many = True)
                return Response(serializer.data,status.HTTP_200_OK)
            
            else:
                orders = self.queryset.filter(user = request.user)
                customer_orders = self.filter_queryset(orders)
                serializer = self.serializer_class(customer_orders, many=True)
                return Response(serializer.data,status.HTTP_200_OK)
            
        return Response({'message': 'You are not authenticated.'}, status.HTTP_403_FORBIDDEN)
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.groups.filter(name__in = ['Manager','Delivery crew']).exists():
                cart_items = Cart.objects.filter(user = request.user)
                if cart_items.exists():
                    order = Order.objects.create(
                        user = request.user,
                        total = 0,
                        date = date.today()
                    )
                    for item in cart_items:
                        OrderItem.objects.create(
                            order = order,
                            menuitem = item.menuitem,
                            quantity = item.quantity,
                            unit_price = item.unit_price,
                            price = item.price
                        )
                        order.total = order.total + item.price
                    order.save()
                    cart_items.delete()
                    return Response({'message':'Ordered Successfully'}, status.HTTP_200_OK)
                else:
                    return Response({'message':'No item in cart'}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'messege':'You are not authorized'}, status.HTTP_403_FORBIDDEN)
        else:
            return Response({'messege':'You are not authenticated'}, status.HTTP_401_UNAUTHORIZED)
        
#Show Order Item       
@permission_classes([IsAuthenticated])               
@throttle_classes([PerMinuteThrottle, UserRateThrottle]) 
class OrderItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order.user != request.user:
            return Response({'message': 'User does not have any order'}, status.HTTP_403_FORBIDDEN)
        else:
            return super().get(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        self.serializer_class = OrderSerializer
        order = self.get_object()
        if request.user.groups.filter(name = 'Manager').exists():
            serializer = self.serializer_class(order, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'You are not authorized'},  status.HTTP_403_FORBIDDEN) 
    
    def patch(self, request, *args, **kwargs):
        self.serializer_class = OrderSerializer
        order = self.get_object()
        if request.user.groups.filter(name='Manager').exists():
            if not request.data:
                return Response({'message': 'Request must contain data to update.'},  status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(order, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        elif request.user.groups.filter(name = 'Delivery crew').exists():
            if not request.data:
                return Response({'message': 'Request must contain data to update.'},  status.HTTP_400_BAD_REQUEST)
            
            if (len(request.data) == 1 and 'status' not in request.data) or (len(request.data) > 1):
                return Response({'message': 'Only the status field can be updated.'}, status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(order, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'You are not authorized'},  status.HTTP_403_FORBIDDEN) 
    
    def delete(self, request, *args, **kwargs):
        self.serializer_class = OrderSerializer
        order = self.get_object()
        if request.user.groups.filter(name = 'Manager').exists():
            self.perform_destroy(order)
            return Response({'message': 'Order deleted successfully'}, status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not authorized'}, status.HTTP_403_FORBIDDEN)
        