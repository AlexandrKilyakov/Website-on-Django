from django.shortcuts import render, redirect
from log_files.models import Users, Gost
from .forms import UsersForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.urls import resolve

from django.contrib.auth.models import User

from django.contrib.auth.hashers import check_password 

def login(requests):
	error = ""

	if requests.method == "POST":
		form = UsersForm(requests.POST)
		
		try:
			if log_admin(requests):
				gost = Gost.objects.order_by("-gost")
				return redirect('/log_files/')
		except:
			pass


		if form.is_valid():
			if not Users.objects.filter(email=form.data["email"]):
				form.save()
			
			mail = Users.objects.get(email=form.data["email"])

			requests.session['id'] = mail.id

			subject, from_email, to = 'Сслыка на прохождение теста', '', form.data["email"]
			html_body = render_to_string("login/email.html", {"email": form.data["email"], "url": f"{requests.build_absolute_uri()}test"})
			text = strip_tags(html_body)
			msg = EmailMultiAlternatives(subject, text, from_email, [to])
			msg.attach_alternative(html_body, "text/html")
			msg.send()
			return render(requests, 'login/message.html')
		else:
			error = "E-MAIL не верен!"
	
	form = UsersForm()
	
	data = {
	"form": form,
	"error": error
	}
	return render(requests, 'login/main.html', data)

def log_admin(requests):
	if (requests.method == "POST"):
		login_txt = requests.POST["user_login"]
		password_txt = requests.POST["user_password"]

		user = User.objects.all()
		for admin in user:
			if(check_password(password_txt, admin.password) and admin.username == login_txt):
				return True

	return False