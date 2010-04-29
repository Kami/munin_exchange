from django import forms

class ProfileForm(forms.Form):
	first_name = forms.CharField(max_length = 30, label = 'First Name')
	last_name = forms.CharField(max_length = 30, label = 'Last Name')
	#(Optional) Make email unique.
	email = forms.EmailField(label = 'Email Address')
	