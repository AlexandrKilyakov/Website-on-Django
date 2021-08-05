from log_files.models import Users
from django.forms import ModelForm, EmailInput

class UsersForm(ModelForm):
	class Meta:
		model = Users
		fields = ['email']

		widgets = {
		"email": EmailInput(attrs = {
			"class": "email",
			"placeholder": "ВВЕДИТЕ СВОЙ E-MAIL АДРЕС"
			})
		}