from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.conf import settings
from .models import Item, StockHistory
from django.contrib.auth.models import User
from .serializers import UserLoginSerializer, UserRegistrationSerializer, CategorySerializer
from .models import Category
from .models import Item
from .serializers import ItemSerializer
from django.shortcuts import get_object_or_404
from django.db import connection

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get(self, request):
        # Try to get data from cache
        print('helloooooooo')
        cached_categories = cache.get('all_categories')
        
        if cached_categories is None:
            print('not in the cache')
            # If cache is empty, get from database
            categories = Category.objects.all()
            serializer = self.serializer_class(categories, many=True)
            cached_categories = serializer.data
            # Store in cache
            cache.set('all_categories', cached_categories, timeout=300)
        else:
            print('from cache: ', cached_categories)
        return Response({
            'status': 'success',
            'data': cached_categories
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Invalidate the cache
            cache.delete('all_categories')
            return Response({
                'status': 'success',
                'message': 'Category created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemListCreateView(APIView):
    def get(self, request):
        cache_key = 'item_list'
        data = cache.get(cache_key)
        if not data:
            items = Item.objects.all()
            data = ItemSerializer(items, many=True).data
            cache.set(cache_key, data, timeout=300)
        return Response(data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete('item_list')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetailView(APIView):
    def get(self, request, pk):
        cache_key = f"item_{pk}"
        data = cache.get(cache_key)
        if not data:
            item = get_object_or_404(Item, pk=pk)
            data = ItemSerializer(item).data
            cache.set(cache_key, data, timeout=300)
        return Response(data)

    def put(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            cache_key = f"item_{pk}"
            cache.set(cache_key, data, timeout=300)
            cache.delete("item_list")
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        cache.delete(f"item_{pk}")
        cache.delete("item_list")
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddRemoveStockView(APIView):
    def put(self, request):
        item_id = request.data.get('item_id')
        action = request.data.get('action')
        change_amount = request.data.get('change_amount')

        if not all([item_id, action, change_amount]):
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, id=item_id)

        if action == 'ADD':
            item.quantity += int(change_amount)
        elif action == 'REMOVE':
            if item.quantity < int(change_amount):
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity -= int(change_amount)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        item.save()

        user = request.user if request.user.is_authenticated else User.objects.first()
        StockHistory.objects.create(
            item=item,
            user=user,
            action=action,
            change_amount=change_amount,
               )

        item_list = cache.get("item_list")
        if item_list:
            for i in item_list:
                if i.get("id") == item.id:
                    i["quantity"] = item.quantity
                    break
            cache.set("item_list", item_list, timeout=300)

        item_data = ItemSerializer(item).data
        cache.set(f"item_{item.id}", item_data, timeout=300)

        return Response({
            'message': f'Stock successfully {action.lower()}ed.',
            'item_id': item.id,
            'new_quantity': item.quantity
        }, status=status.HTTP_200_OK)

class InventorySummary(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            # Total item count and total value
            cursor.execute("""
                SELECT
                    SUM(quantity) AS total_items_count,
                    SUM(quantity * price) AS total_value
                FROM inventory_control_item
            """)
            total_items_count, total_value = cursor.fetchone()

            # Items low in stock
            cursor.execute("""
                SELECT name, quantity
                FROM inventory_control_item
                WHERE quantity < 10
            """)
            items_low_in_stock = [
                {"name": row[0], "quantity": row[1]}
                for row in cursor.fetchall()
            ]

        data = {
            "total_items_count": total_items_count or 0,
            "total_value": float(total_value or 0),
            "items_low_in_stock": items_low_in_stock
        }

        return Response(data, status=status.HTTP_200_OK)    