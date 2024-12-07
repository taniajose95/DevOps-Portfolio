from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import SignUpForm
from .models import CustomUser, Booking, Approval, RoomAvailability, Room
from django.shortcuts import render, redirect
from .models import Approval, Booking
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def user_logout(request):
    logout(request)
    return redirect(reverse('user_login'))

def authenticate_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Authentication successful'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            role = form.cleaned_data.get('role')
            department = form.cleaned_data.get('department')
            password = form.cleaned_data.get('password1')
            print(name)
            print(email)
            print(role)
            print(department)
            try:
                user = CustomUser.objects.create_user(email=email, name=name, role=role, department=department, password=password)
                # Create a new user instance
                # user = CustomUser.objects.create_user(email=email, name=name, role=role, department=department, password=password)
                # user.email =email
                # user.name = name
                # user.role = role
                # user.department = department
                # user.save()
            except Exception as e:
                # Print the specific error message
                print(f"Error occurred during user creation: {e}")
                return HttpResponseBadRequest("Error occurred during user creation.")

            # Redirect the user to the login page after successful signup
            return redirect('user_login')
        else:
            # Print form errors if the form is not valid
            print("Form errors:", form.errors)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user using Django's authentication system
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Authentication successful, log in the user
            login(request, user)
            # Redirect user to the desired page (e.g., 'index')
            return redirect('index')
        else:
            # Invalid login credentials, display an error message
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')
    else:
        # Render the login page for GET requests
        return render(request, 'login.html')

def index(request):
    # You can add any context data needed for rendering the template
    # user_role = request.customuser.Role.lower() if request.customuser.Role else ''
    context = {
        'welcome_message': 'Welcome to Classroom Pro application!',
    }
    return render(request, 'index.html',  {'customuser': request.user})


def room_list(request):
    rooms = Room.objects.all()
    if request.method == 'GET':
        room_name = request.GET.get('room_name')
        capacity = request.GET.get('capacity')
        location = request.GET.get('location')

        # Filter rooms based on form inputs
        if room_name:
            rooms = rooms.filter(RoomName__icontains=room_name)
        if capacity:
            rooms = rooms.filter(Capacity__gte=int(capacity))
        if location:
            rooms = rooms.filter(Location__icontains=location)
    print(rooms)
    return render(request, 'room_list.html', {'rooms': rooms})


def book_room(request, room_id):
    if request.method == 'POST':
        # Get the user_id of the currently logged-in user
        user_id = request.user.UserID

        # Assuming other form data is submitted via POST
        date = request.POST['date']
        time_slot = request.POST['time_slot']

        room = Room.objects.get(pk=room_id)
        user = CustomUser.objects.get(pk=user_id)

        # Check if the room is available for booking
        if Booking.objects.filter(Room=room, Date=date, TimeSlot=time_slot).exists():
            messages.error(request, 'The room is already booked for this time slot.')
            return redirect('room_list')
        else:
            booking = Booking.objects.create(Room=room, User=user, Date=date, TimeSlot=time_slot, Status='Pending' )
            messages.success(request, 'Room booked successfully.')
            return redirect('room_list')
    else:
        room = Room.objects.get(pk=room_id)
        room_availability = RoomAvailability.objects.filter(Room_id=room_id)
        return render(request, 'book_room.html', {'room': room, 'room_availability': room_availability})

def manage_booking(request):
    # Fetch bookings from the database
    bookings = Booking.objects.filter(User=request.user)
    return render(request, 'manage_booking.html', {'bookings': bookings})

def cancel_booking(request, booking_id):
    booking = Booking.objects.get(BookingID=booking_id)
    # Delete the booking
    booking.delete()
    return redirect('manage_booking')

def modify_booking(request, booking_id):
    booking = Booking.objects.get(BookingID=booking_id)
    if request.method == 'POST':
        new_time_slot = request.POST.get('time_slot')
        # Update time slot in Booking table
        booking.TimeSlot = new_time_slot
        booking.save()
        # Update availability status in RoomAvailability table (assuming you want to mark the old slot as available)
        old_time_slot_availability = RoomAvailability.objects.get(Room_id=booking.Room_id, Date=booking.Date, TimeSlot=booking.TimeSlot)
        old_time_slot_availability.AvailabilityStatus = 'available'
        old_time_slot_availability.save()
        new_time_slot_availability = RoomAvailability.objects.get(Room_id=booking.Room_id, Date=booking.Date, TimeSlot=new_time_slot)
        new_time_slot_availability.AvailabilityStatus = 'booked'
        new_time_slot_availability.save()
        return redirect('manage_booking')
    else:
        room_availabilities = RoomAvailability.objects.filter(Room_id=booking.Room_id, AvailabilityStatus='available')
        return render(request, 'modify_booking.html', {'room_availabilities': room_availabilities})


def approval_page(request):
    if request.user.Role.lower() == 'admin':
        bookings = Booking.objects.all()  # Retrieve all booking records
        bookings_with_details = []

        for booking in bookings:
            user = CustomUser.objects.get(UserID=booking.User_id)
            room = Room.objects.get(RoomID=booking.Room_id)
            booking_details = {
                'booking_id': booking.BookingID,
                'status': booking.Status,
                'date': booking.Date,
                'time_slot': booking.TimeSlot,
                'user_name': user.Name,  # Assuming User model has a 'name' field
                'room_name': room.RoomName,  # Assuming Room model has a 'name' field
            }
            bookings_with_details.append(booking_details)

        return render(request, 'approval.html', {'bookings': bookings_with_details})
    else:
        return render(request, 'not_authorized.html')




def approve_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        comments = request.POST.get('comments')

        if action in ['approve', 'reject']:
            try:
                booking = Booking.objects.get(BookingID=booking_id)
            except Booking.DoesNotExist:
                messages.error(request, 'Booking not found.')
                return redirect('approval_page')

            approval_status = 'approved' if action == 'approve' else 'rejected'

            # Retrieve all Approval records for the given Booking
            approvals = Approval.objects.filter(Booking=booking)

            # Update or create new Approval records for the Booking
            for approval in approvals:
                approval.ApprovalStatus = approval_status
                approval.Comments=comments
                approval.ApprovedBy = request.user  # Assuming request.user is the CustomUser instance
                approval.save()

            # Update the booking status if needed
            booking.Status = approval_status
            booking.Comments = comments
            booking.save()

            availability_status = 'booked' if approval_status == 'approved' else 'available'
            room_availability = RoomAvailability.objects.filter(Room=booking.Room, Date=booking.Date,
                                                                TimeSlot=booking.TimeSlot)
            if room_availability.exists():
                room_availability.update(AvailabilityStatus=availability_status)
            else:
                RoomAvailability.objects.create(Room=booking.Room, Date=booking.Date, TimeSlot=booking.TimeSlot,
                                                AvailabilityStatus=availability_status)

            # Display success message
            #if action == 'approve':
                #message= messages.success(request, 'Booking approved successfully.')
            #else:
                #message = messages.success(request, 'Booking rejected successfully.')

            # Redirect to the approval result page
            return render(request, 'approve_booking.html', {
                'action': action,
                #'success_message': message
            })

    # If request method is not POST or action is invalid, redirect to approval page
    return redirect('approval_page')
def reject_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        # Update the booking status and reason
        booking.status = 'Rejected'
        booking.save()

        # Record rejection in UserApproval table
        Approval.objects.create(user=booking.user, booking=booking, status='Rejected', reason=reason)

        # Update other tables as needed

        # Redirect to home page with a notification
        return redirect('index', notification=f'Booking for {booking.date} - {booking.time_slot} rejected.')

    return render(request, 'reject_booking.html', {'booking': booking})

