from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Room, Booking
from decimal import Decimal
import uuid
from datetime import datetime
from django.conf import settings
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def home(request):
    return render(request, "main/index.html")


def rooms(request):
    rooms_qs = Room.objects.all()
    return render(request, "main/rooms.html", {"rooms": rooms_qs})


def events(request):
    return render(request, "main/events.html")


def gallery(request):
    return render(request, "main/gallery.html")


def about(request):
    return render(request, "main/about.html")


def contact(request):
    return render(request, "main/contact.html")


def room_detail(request, slug):
    room = get_object_or_404(Room, slug=slug)
    context = {"room": room}
    if request.method == "POST":
        print("[ROOM_DETAIL] POST", {"room": room.slug})
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")
        guests_str = request.POST.get("guests", "1")
        try:
            guests = int(guests_str)
        except ValueError:
            guests = 1

        try:
            ci = datetime.strptime(check_in, "%Y-%m-%d").date()
            co = datetime.strptime(check_out, "%Y-%m-%d").date()
        except Exception:
            print("[ROOM_DETAIL] Bad dates", {"check_in": check_in, "check_out": check_out})
            context["error"] = "Please provide valid check-in and check-out dates."
            return render(request, "main/room-detail.html", context)

        if co <= ci:
            print("[ROOM_DETAIL] Date order invalid", {"check_in": ci, "check_out": co})
            context["error"] = "Check-out must be after check-in."
            return render(request, "main/room-detail.html", context)

        if guests > room.max_guests:
            print("[ROOM_DETAIL] Guests exceed capacity", {"guests": guests, "max": room.max_guests})
            context["error"] = "Selected guests exceed the room capacity."
            return render(request, "main/room-detail.html", context)

        if Booking.objects.filter(room=room, check_in__lt=co, check_out__gt=ci).exists():
            print("[ROOM_DETAIL] Overlap", {"room_id": room.id, "check_in": ci, "check_out": co})
            context["error"] = "This room is already booked for the selected dates."
            return render(request, "main/room-detail.html", context)

        nights = (co - ci).days
        total = (Decimal(nights) * room.price_per_night)
        reference = f"BK-{uuid.uuid4().hex[:10].upper()}"
        print("[ROOM_DETAIL] Computed", {"nights": nights, "total": str(total), "reference": reference})
        session_key = f"PAY_{reference}"
        request.session[session_key] = {
            "room_id": room.id,
            "check_in": ci.strftime("%Y-%m-%d"),
            "check_out": co.strftime("%Y-%m-%d"),
            "guests": guests,
            "amount": str(total),
            "user_id": request.user.id if request.user.is_authenticated else None,
        }
        request.session.save()
        print("[ROOM_DETAIL] Intent stored", {"session_key": session_key})
        return redirect("payment_init", reference=reference)

    return render(request, "main/room-detail.html", context)


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "main/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm(request)
    return render(request, "main/login.html", {"form": form})


def payment_init(request, reference):
    session_key = f"PAY_{reference}"
    payload = request.session.get(session_key)
    if not payload:
        print("[PAYMENT_INIT] Missing payload", {"reference": reference})
        return redirect("home")
    user = None
    name = ""
    email = ""
    phone = ""
    user_id = payload.get("user_id")
    if user_id:
        # Lazy import to avoid circulars
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            name = user.get_full_name() or user.username
            email = user.email or ""
            phone = getattr(user, "phone_number", "") or ""
        except User.DoesNotExist:
            pass
    amount = float(payload.get("amount"))
    print("[PAYMENT_INIT] Render", {"reference": reference, "amount": amount})
    context = {
        "public_key": settings.FLUTTERWAVE_PUBLIC_KEY,
        "tx_ref": reference,
        "amount": amount,
        "currency": "NGN",
        "customer_name": name or "Guest",
        "customer_email": email or "guest@example.com",
        "customer_phone": phone,
        "title": "Jonggrand Hotel",
        "logo": "/static/assets/images/logo.png",
        "redirect_url": "",
    }
    return render(request, "main/payment.html", context)


def payment_verify(request):
    transaction_id = request.GET.get("transaction_id") or request.GET.get("id")
    tx_ref = request.GET.get("tx_ref")
    if not transaction_id or not tx_ref:
        # Fallback to verify by reference
        verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
        req = Request(verify_url)
        req.add_header("Authorization", f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}")
        try:
            resp = urlopen(req)
            payload = resp.read().decode("utf-8")
            data = json.loads(payload)
            status = data.get("status")
            inner = data.get("data") or {}
            processor_status = inner.get("status")
            tx_check = inner.get("tx_ref")
            amount_paid = inner.get("amount")
            currency = inner.get("currency")
            print("[PAYMENT_VERIFY][ref]", {"status": status, "processor_status": processor_status, "tx_check": tx_check, "amount": amount_paid, "currency": currency})
            if status == "success" and processor_status == "successful" and tx_check == tx_ref:
                return _finalize_booking(request, tx_ref, amount_paid, currency)
        except (URLError, HTTPError, json.JSONDecodeError) as e:
            print("[PAYMENT_VERIFY][ref] error", {"error": str(e)})
            return redirect("home")
        return redirect("home")
    else:
        url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        req = Request(url)
        req.add_header("Authorization", f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}")
        try:
            resp = urlopen(req)
            payload = resp.read().decode("utf-8")
            data = json.loads(payload)
            status = data.get("status")
            inner = data.get("data") or {}
            processor_status = inner.get("status")
            tx_check = inner.get("tx_ref")
            amount_paid = inner.get("amount")
            currency = inner.get("currency")
            print("[PAYMENT_VERIFY][id]", {"status": status, "processor_status": processor_status, "tx_check": tx_check, "amount": amount_paid, "currency": currency})
            if status == "success" and processor_status == "successful" and tx_check == tx_ref:
                return _finalize_booking(request, tx_ref, amount_paid, currency)
        except (URLError, HTTPError, json.JSONDecodeError) as e:
            print("[PAYMENT_VERIFY][id] error", {"error": str(e)})
            return redirect("home")
        return redirect("home")


def _finalize_booking(request, tx_ref, amount_paid, currency):
    session_key = f"PAY_{tx_ref}"
    payload = request.session.get(session_key)
    if not payload:
        print("[FINALIZE] Missing session", {"reference": tx_ref})
        return redirect("home")
    if currency != "NGN":
        print("[FINALIZE] Currency mismatch", {"currency": currency})
        return redirect("home")
    expected_amount = Decimal(payload["amount"])
    try:
        if Decimal(str(amount_paid)) < expected_amount:
            print("[FINALIZE] Amount mismatch", {"paid": amount_paid, "expected": str(expected_amount)})
            return redirect("home")
    except Exception:
        print("[FINALIZE] Amount parse error", {"paid": amount_paid})
        return redirect("home")
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = None
    if payload.get("user_id"):
        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            user = None
    room = get_object_or_404(Room, id=payload["room_id"])
    ci = datetime.strptime(payload["check_in"], "%Y-%m-%d").date()
    co = datetime.strptime(payload["check_out"], "%Y-%m-%d").date()
    guests = int(payload["guests"])
    if Booking.objects.filter(room=room, check_in__lt=co, check_out__gt=ci).exists():
        print("[FINALIZE] Overlap at finalize", {"room_id": room.id, "check_in": ci, "check_out": co})
        return redirect("home")
    Booking.objects.create(
        user=user,
        room=room,
        check_in=ci,
        check_out=co,
        guests=guests,
        total_amount=expected_amount,
        status=Booking.STATUS_PAID,
        reference=tx_ref,
    )
    try:
        del request.session[session_key]
        request.session.save()
    except KeyError:
        pass
    print("[FINALIZE] Created", {"reference": tx_ref})
    return redirect("payment_success", reference=tx_ref)


def payment_success(request, reference):
    booking = get_object_or_404(Booking, reference=reference, status=Booking.STATUS_PAID)
    return render(request, "main/payment_success.html", {"booking": booking})
