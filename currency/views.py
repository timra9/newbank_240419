from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse
from .models import Currency
from .serializer import CurrencySerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status

# Create your views here.
def index(request):
    currencies = Currency.objects.all()
    return render(request, 'currency/index.html', 
                  {'currencies': currencies})

@csrf_exempt
def currency_api(request):
    if request.method == 'GET':
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CurrencySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return HttpResponseNotFound()

def exchange_api(request):
    from_code = request.GET.get('from')
    to_code = request.GET.get('to')
    amount = request.GET.get('amount')
    if not amount:
        return JsonResponse({'error': 'Amount is required'}, status=400)
    amount = float(amount)
    
    from_currency = Currency.objects.filter(code=from_code).first()

    if not from_currency:
        return JsonResponse({'error': 'From currency not found'}, status=400)
    
    to_currency = Currency.objects.filter(code=to_code).first()
    if not to_currency:
        return JsonResponse({'error': 'To currency not found'}, status=400)
    # Convert amount to USD first, then to target currency
    amount_in_usd = float(amount) / float(from_currency.rate_to_usd)
    converted_amount = amount_in_usd * float(to_currency.rate_to_usd)
    
    return JsonResponse({'result': converted_amount})
