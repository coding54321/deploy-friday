from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import User, Cafe, Seat, Favorite, Reservation
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from geopy.distance import distance
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from .forms import SocialSignupForm
import json
from datetime import timedelta
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from .forms import UserSignupForm
import pytz
from django.urls import reverse
from django.urls import reverse_lazy
from .forms import UserSignupForm
from main.forms import UserSignupForm
from allauth.account.views import SignupView as AllauthSignupView
from django.urls import reverse_lazy
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.helpers import complete_social_login
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.account.utils import complete_signup
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.helpers import complete_social_login
from django.http import HttpResponseBadRequest
from django.contrib.auth import login as auth_login
from .models import User
from .forms import SocialSignupForm
from allauth.socialaccount.models import SocialAccount


class CustomSignupView(AllauthSignupView):
    form_class = UserSignupForm
    template_name = 'account/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        return complete_signup(self.request, user, app_settings.EMAIL_VERIFICATION, self.get_success_url())

def home(request):
    areas = ['정후', '참살이', '정문', '제기동', '개운사길', '옆살이', '이공계']
    nearby_cafes = []

    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    if user_lat and user_lng:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
        for cafe in Cafe.objects.all():
            if cafe.latitude and cafe.longitude:
                cafe_location = (cafe.latitude, cafe.longitude)
                user_location = (user_lat, user_lng)
                dist = distance(user_location, cafe_location).km
                if dist <= 3:
                    nearby_cafes.append({
                        'cafe_id': cafe.cafe_id,
                        'cafe_name': cafe.cafe_name,
                        'cafe_time': cafe.cafe_time,
                        'empty_seats': cafe.empty_seats,
                        'cafe_photo': cafe.cafe_photo.url if cafe.cafe_photo else '',
                        'distance': round(dist, 2)
                    })

    context = {
        'areas': areas,
        'nearby_cafes': nearby_cafes,
    }
    return render(request, 'home.html', context)

def region_cafes(request, region_name):
    cafes = Cafe.objects.filter(cafe_region=region_name)
    context = {
        'region_name': region_name,
        'cafes': cafes,
    }
    return render(request, 'region.html', context)

def nearby_cafes(request):
    user_lat = float(request.GET.get('lat'))
    user_lng = float(request.GET.get('lng'))

    cafes = []
    for cafe in Cafe.objects.all():
        if cafe.latitude and cafe.longitude:
            cafe_location = (cafe.latitude, cafe.longitude)
            user_location = (user_lat, user_lng)
            dist = distance(user_location, cafe_location).km
            if dist <= 3:
                cafes.append({
                    'cafe_id': cafe.cafe_id,
                    'cafe_name': cafe.cafe_name,
                    'cafe_time': cafe.cafe_time,
                    'empty_seats': cafe.empty_seats,
                    'cafe_photo': cafe.cafe_photo.url if cafe.cafe_photo else '',
                    'distance': round(dist, 2)
                })

    return JsonResponse(cafes, safe=False)

def all_cafes(request):
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    cafes = []
    for cafe in Cafe.objects.all():
        cafe_data = {
            'cafe_id': cafe.cafe_id,
            'cafe_name': cafe.cafe_name,
            'cafe_time': cafe.cafe_time,
            'empty_seats': cafe.empty_seats,
            'cafe_photo': cafe.cafe_photo.url if cafe.cafe_photo else '',
        }
        
        if user_lat and user_lng and cafe.latitude and cafe.longitude:
            user_location = (float(user_lat), float(user_lng))
            cafe_location = (cafe.latitude, cafe.longitude)
            dist = distance(user_location, cafe_location).km
            cafe_data['distance'] = round(dist, 2)
        else:
            cafe_data['distance'] = None
        
        cafes.append(cafe_data)
    
    # 거리 정보가 있는 경우에만 정렬
    cafes_with_distance = [c for c in cafes if c['distance'] is not None]
    cafes_without_distance = [c for c in cafes if c['distance'] is None]
    
    sorted_cafes = sorted(cafes_with_distance, key=lambda x: x['distance']) + cafes_without_distance

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(sorted_cafes, safe=False)
    else:
        context = {
            'region_name': '전체',
            'cafes': sorted_cafes,
        }
        return render(request, 'region.html', context)
    
def cafe_detail(request, id):
    cafe = get_object_or_404(Cafe, id=id)
    seats = Seat.objects.filter(cafe=cafe)
    is_liked = False
    
    if request.user.is_authenticated:
        is_liked = Favorite.objects.filter(user=request.user, cafe=cafe, liked=True).exists()
    
    if request.method == 'POST' and request.user.is_authenticated:
        favorite, created = Favorite.objects.get_or_create(user=request.user, cafe=cafe)
        favorite.liked = not favorite.liked
        favorite.save()
        return JsonResponse({'success': True, 'liked': favorite.liked})
    
    return render(request, 'cafe_detail.html', {'cafe': cafe, 'seats': seats, 'is_liked': is_liked})

def cafe_region(request, region_id):
    cafes = Cafe.objects.filter(cafe_region=region_id)
    return render(request, 'cafe_region.html', {'cafes': cafes})

def search(request):
    query = request.GET.get('q')
    if query:
        cafes = Cafe.objects.filter(Q(cafe_name__icontains=query))
    else:
        cafes = Cafe.objects.all()
    return render(request, 'search.html', {'cafes': cafes, 'query': query})

def ajax_search(request):
    query = request.GET.get('q', '')
    plug_filter = request.GET.get('plug') == 'true'
    backseat_filter = request.GET.get('backseat') == 'true'
    filters_applied = request.GET.get('filtersApplied') == 'true'

    cafes = Cafe.objects.all()

    if query:
        cafes = cafes.filter(Q(cafe_name__icontains(query)) | Q(cafe_address__icontains(query)))

    if filters_applied:
        if plug_filter and backseat_filter:
            cafes = cafes.filter(seat__seat_status='available', seat__plug=True, seat__backseat=True).distinct()
        elif plug_filter:
            cafes = cafes.filter(seat__seat_status='available', seat__plug=True).distinct()
        elif backseat_filter:
            cafes = cafes.filter(seat__seat_status='available', seat__backseat=True).distinct()

    results = [{'id': cafe.id, 'cafe_name': cafe.cafe_name, 'cafe_address': cafe.cafe_address} for cafe in cafes]
    return JsonResponse(results, safe=False)


@login_required
def user_likes(request, user_id):
    user = get_object_or_404(User, id=user_id)
    likes = Favorite.objects.filter(user=user, liked=True).select_related('cafe')  # select_related를 사용하여 관련된 cafe 객체를 미리 불러옵니다.
    return render(request, 'user_likes.html', {'user': user, 'likes': likes})


@login_required
def like_cafe(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    user = request.user
    favorite, created = Favorite.objects.get_or_create(user=user, cafe=cafe)
    
    if not created:
        favorite.liked = not favorite.liked
        favorite.save()
    else:
        favorite.liked = True
        favorite.save()

    return JsonResponse({'success': True, 'liked': favorite.liked})

# 회원가입 커스텀뷰 오버라이드
# class CustomSignupView(SignupView):
#     form_class = UserSignupForm
#     template_name = 'account/signup.html'
#     success_url = reverse_lazy('home')


@login_required
def user_profile(request, user_id):
    if user_id == 0:
        return redirect('user_login')
    
    user = get_object_or_404(User, id=user_id)
    
    current_reservations = Reservation.objects.filter(
        user=user,
        seat__seat_status__in=['requesting', 'reserved', 'occupied']
    ).order_by('reservation_time')
    
    past_reservations = Reservation.objects.filter(
        user=user,
        seat__seat_status='available'
    ).order_by('-reservation_time')
    
    has_active_reservation = current_reservations.exists()

    try:
        social_account = SocialAccount.objects.get(user=user)
        extra_data = social_account.extra_data
        # Check for Kakao account nickname
        if 'kakao_account' in extra_data:
            nickname = extra_data['kakao_account']['profile']['nickname']
        # Check for Naver account nickname
        elif 'name' in extra_data:
            nickname = extra_data['name']
        else:
            nickname = ''
    except SocialAccount.DoesNotExist:
        nickname = ''

    context = {
        'user': user,
        'nickname': nickname,
        'current_reservations': current_reservations,
        'past_reservations': past_reservations,
        'has_active_reservation': has_active_reservation,
    }
    return render(request, 'user_profile.html', context)

def user_signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                messages.success(request, '회원가입이 완료되었습니다.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'오류 발생: {str(e)}')
        else:
            messages.error(request, '양식을 올바르게 작성해주세요.')
    else:
        form = UserSignupForm()
    return render(request, 'account/signup.html', {'form': form})

def social_signup(request):
    if request.method == 'POST':
        form = SocialSignupForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                user = request.user
                user.name = form.cleaned_data['name']
                user.telephone = form.cleaned_data['telephone']
                user.save()

                # 로그인 처리 후 홈으로 리다이렉트
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            else:
                return HttpResponseBadRequest('사용자가 인증되지 않았습니다.')
        else:
            return render(request, 'social_signup.html', {'form': form})
    else:
        form = SocialSignupForm()
        return render(request, 'social_signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        user = User.objects.filter(user_id=user_id).first()
        if user is not None and user.check_password(password):
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')  
        else:
            if User.objects.filter(user_id=user_id).exists():
                messages.error(request, '비밀번호를 잘못 입력했습니다.')
            else:
                messages.error(request, '등록되지 않은 ID입니다.')
    return render(request, 'account/login.html')


@login_required
def user_logout(request):
    auth_logout(request)
    return redirect('home')

# 예약
@login_required
def seat_map(request, id):
    cafe = get_object_or_404(Cafe, id=id)
    seats = Seat.objects.filter(cafe_id=id)
    template_name = f'seat_map/seat_map_{id}.html' 
    
    return render(request, template_name, {'cafe': cafe, 'seats': seats})

@login_required
def reservation_create(request, cafe_id, seat_id):
    user = request.user
    cafe = get_object_or_404(Cafe, id=cafe_id)
    seats = Seat.objects.filter(cafe_id=cafe_id)
    template_name = f'seat_map/seat_map_{cafe_id}.html'

    has_active_reservation = Reservation.objects.filter(
        user=user,
        seat__seat_status__in=['requesting', 'reserved', 'occupied']
    ).exists()
    
    if has_active_reservation:
        messages.error(request, '이미 예약/사용 중인 좌석이 있습니다.')
        return redirect('user_profile', user_id=user.id)
    
    if request.method == 'POST':
        seat = get_object_or_404(Seat, id=seat_id)
 
        reservation = Reservation.objects.create(
            user=user,
            cafe=cafe,
            seat=seat,
            reservation_time=timezone.now(),
            number_of_people=request.POST.get('number_of_people')
        )

        seat.seat_status = 'requesting'
        seat.save()

        messages.success(request, f'{cafe.cafe_name}의 좌석 {seat.seats_no}번 예약이 완료되었습니다.')
        
        return redirect('reservation_success')

    return render(request, template_name, {'cafe': cafe, 'seats': seats})

def reservation_success(request):
    return render(request, 'reservation_success.html') 

@login_required
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'reservation_detail.html', {'reservation': reservation})

def startview(request):
    return render(request, 'start.html')

# 카페 로그인
def cafe_login(request):
    if request.method == 'POST':
        cafe_id = request.POST.get('cafe_id')
        cafe_pw = request.POST.get('cafe_pw')
        try:
            cafe = Cafe.objects.get(cafe_id=cafe_id)
            if cafe.cafe_pw == cafe_pw:
                # 로그인 성공 처리
                request.session['cafe_id'] = cafe.id
                return redirect('dashboard_overview', cafe_id=cafe.id)  # 로그인 후 리다이렉트할 페이지
            else:
                messages.error(request, '비밀번호가 올바르지 않습니다.')
        except Cafe.DoesNotExist:
            messages.error(request, '존재하지 않는 카페 ID입니다.')
    return render(request, 'cafe_login.html')

@login_required
def seat_overview(request, cafe_id):
    seats = Seat.objects.filter(cafe_id=cafe_id)
    cafe = get_object_or_404(Cafe, id=cafe_id)
    reservations = Reservation.objects.filter(seat__cafe_id=cafe_id)
    return render(request, 'reservations/seat_overview.html', {'cafe': cafe, 'seats': seats, 'reservations': reservations, 'user': request.user})

@login_required
def update_seat_status(request, seat_id):
    if request.method == 'POST':
        try:
            seat = get_object_or_404(Seat, id=seat_id)
            data = json.loads(request.body)
            status = data.get('status')

            if status == 'occupied':
                seat.seat_status = 'occupied'
                seat.seat_start_time = timezone.now()
            elif status == 'reserved':
                seat.seat_status = 'reserved'
                seat.reserved_by = request.user
            elif status == 'available':
                seat.seat_status = 'available'
                seat.seat_start_time = None
                seat.reserved_by = None
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

            seat.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def confirm_reservation(request, reservation_id, seat_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, seat__id=seat_id)
    seat = reservation.seat
    seat_id = reservation.seat.id
    seat.seat_status = 'reserved'
    seat.save()
    
    return redirect('seat_overview', cafe_id=seat.cafe.id)

@login_required
def cancel_reservation(request, reservation_id, cafe_id, *args, **kwargs):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    seat = reservation.seat
    seat_id = reservation.seat.id
    seat.seat_status = 'available'
    reservation.delete()
    seat.save()
    
    return redirect(reverse('seat_overview', kwargs={'cafe_id': cafe_id}))

@login_required
def seat_check(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    if seat.seat_status == 'reserved':
        seat.seat_status = 'occupied'
        seat.seat_start_time = timezone.now()
    seat.save()
    return redirect('seat_overview')

@login_required
def check_active_reservation(request):
    has_active_reservation = Reservation.objects.filter(
        user=request.user,
        seat__seat_status__in=['requesting', 'reserved', 'occupied']
    ).exists()
    return JsonResponse({'has_active_reservation': has_active_reservation})

@login_required
def dashboard_overview(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    seoul_tz = pytz.timezone('Asia/Seoul')
    today = timezone.now().astimezone(seoul_tz)
    
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=7)

    reservations_week = Reservation.objects.filter(
        cafe=cafe, 
        reservation_time__date__range=(start_of_week.date(), end_of_week.date())
    )
    reservations_by_day = reservations_week.extra({'day': "DAYOFWEEK(reservation_time)"}).values('day').annotate(count=Count('id')).order_by('day')
    
    # 요일과 예약 수 초기화
    days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    counts = [0] * 7

    # 각 요일에 대한 예약 수 채우기
    for res in reservations_by_day:
        day = int(res['day']) - 1  # MySQL의 DAYOFWEEK는 1(일요일)부터 7(토요일)까지 반환합니다.
        counts[day] = res['count']
        
    # 시간대별 예약
    reservations_today = Reservation.objects.filter(cafe=cafe, reservation_time__date=today.date())
    reservations_by_hour = reservations_today.extra({'hour': "HOUR(reservation_time)"}).values('hour').annotate(count=Count('id')).order_by('hour')
    hours = list(range(10, 23))
    counts_by_hour = [0] * len(hours)
    
    for res in reservations_by_hour:
        hour = int(res['hour'])
        counts_by_hour[hour - 10] = res['count']

    # 가장 많은 예약이 있는 시간 결정
    max_hour = None
    if counts_by_hour:
        max_count = max(counts_by_hour)
        max_hour = hours[counts_by_hour.index(max_count)]
        
    # 좋아요 누른 고객 수
    favorite_count = Favorite.objects.filter(cafe=cafe, liked=True).count()

    # 오늘 예약 생성 수
    today_reservations_count = reservations_today.count()

    context = {
        'cafe': cafe,
        'favorite_count': favorite_count,
        'today_reservations_count': today_reservations_count,
        'hours': hours,
        'counts_by_hour': counts_by_hour,
        'max_hour': max_hour,
        'days_of_week': days_of_week,
        'counts': counts,
    }

    return render(request, 'dashboard/overview.html', context)
