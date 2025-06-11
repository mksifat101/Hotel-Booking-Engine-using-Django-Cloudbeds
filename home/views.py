import requests
import stripe
from decouple import config
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt


stripe.api_key = config("STRIPE_API_KEY")

# Create your views here.
def home_home(request):
    url = "https://api.cloudbeds.com/api/v1.2/getHotels"

    headers = {
        "accept": "application/json",
        "x-api-key": config('CLOUDBEDS_API_KEY')
    }
    response = requests.get(url, headers=headers)

    res_json = response.json()

    hotels = res_json.get("data", [])

    data = {
        'hotels': hotels,
    }
    return render(request, 'home/home.html', data)



def home_hotel_single(request, id):
    url = f"https://api.cloudbeds.com/api/v1.2/getHotelDetails?propertyID={id}"

    headers = {
        "accept": "application/json",
        "x-api-key": config('CLOUDBEDS_API_KEY')
    }

    response = requests.get(url, headers=headers)

    res_json = response.json()

    # print(response.text)

    hotel = res_json.get("data", [])

    hotel_thumb = hotel.get('propertyImage', [])
    hotel_image4 = hotel.get('propertyAdditionalPhotos', [])[:4]
    hotel_image_all = hotel.get('propertyAdditionalPhotos', [])
    if request.method == "get":
        room_url = f"https://api.cloudbeds.com/api/v1.2/getAvailableRoomTypes?propertyIDs={id}&startDate=2025-06-06&endDate=2025-06-08"

        room_headers = {
            "accept": "application/json",
            "x-api-key": config('CLOUDBEDS_API_KEY')
        }

        room_response = requests.get(room_url, headers=room_headers)
        
        room_res_json = response.json()

        rooms = room_res_json.get("data", [])

        print(room_response.text)

    data = {
        'hotel': hotel,
        'hotel_image4': hotel_image4,
        'hotel_image_all': hotel_image_all,
        'hotel_thumb': hotel_thumb,
    }
    return render(request, 'home/home_single.html', data)




def home_hotel_single_search(request, id):
    url = f"https://api.cloudbeds.com/api/v1.2/getHotelDetails?propertyID={id}"

    headers = {
        "accept": "application/json",
        "x-api-key": config('CLOUDBEDS_API_KEY')
    }

    response = requests.get(url, headers=headers)

    res_json = response.json()

    # print(response.text)

    hotel = res_json.get("data", [])

    hotel_thumb = hotel.get('propertyImage', [])
    hotel_image4 = hotel.get('propertyAdditionalPhotos', [])[:4]
    hotel_image_all = hotel.get('propertyAdditionalPhotos', [])

    print(response.text)

    checkin_date = request.GET.get('checkin_date')
    checkout_date = request.GET.get('checkout_date')
    if checkin_date and checkout_date:
        room_url = f"https://api.cloudbeds.com/api/v1.2/getAvailableRoomTypes?propertyIDs={id}&startDate={checkin_date}&endDate={checkout_date}"
        room_response = requests.get(room_url, headers=headers)
        room_res_json = room_response.json()
        rooms = room_res_json.get("data", [])
        for room in rooms:
            rooms_pp = room.get("propertyRooms")
            for roomt in rooms_pp:
                rooms_thumb = roomt.get('roomTypePhotos')[:1]
                room_id = roomt.get("roomTypeID")

            for roomp in rooms_pp:
                price = roomp.get('roomRate')

    data = {
        'hotel': hotel,
        'hotel_image4': hotel_image4,
        'hotel_image_all': hotel_image_all,
        'hotel_thumb': hotel_thumb,
        'rooms': rooms,
        'rooms_thumb': rooms_thumb,
        'price': price,
        'room_id': room_id,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
    }
    return render(request, 'home/home_single.html', data)



def home_hotel_booking(request):
    if request.method == "POST":
        property_id = request.POST.get('property_id')
        room_id = request.POST.get('room_id')
        checkin_date = request.POST.get('checkin_date')
        checkout_date = request.POST.get('checkout_date')
        amount = request.POST.get('amount')  
        property_name = request.POST.get('property_name')
        property_img = request.POST.get('property_img')

    data = {
        'property_id': property_id,
        'room_id': room_id,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'amount': amount,
        'property_name': property_name,
        'property_img': property_img,
    }
    return render(request, 'home/home_booking.html', data)



def home_hotel_booking_stripe(request):
    if request.method == "POST":
        property_id = request.POST.get('property_id')
        room_id = request.POST.get('room_id')
        checkin_date = request.POST.get('checkin_date')
        checkout_date = request.POST.get('checkout_date')
        amount = int(request.POST.get('amount'))  # Amount in cents

        

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        notes = request.POST.get('notes')

        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                            'name': f"Booking for Room {room_id}",
                            'description': f"Stay from {checkin_date} to {checkout_date}",
                        },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={  # ✅ Safe place for extra fields
                'property_id': property_id,
                'room_id': room_id,
                'checkin_date': checkin_date,
                'checkout_date': checkout_date,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address1': address1,
                'address2': address2,
                'state': state,
                'zip_code': zip_code,
                'notes': notes,
            },
            success_url=request.build_absolute_uri(reverse('home_success')),
            cancel_url=request.build_absolute_uri(reverse('home_cancel')),
        )

        return redirect(session.url, code=303)

    return render(request, 'home/home_booking_stripe.html')



def home_success(request):
    return render(request, 'home/success.html')


def home_cancel(request):
    return redirect('home_home')