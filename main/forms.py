from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class RegistrationForm(UserCreationForm):
    surname = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_surname'
        })
    )
    name = forms.CharField(
        label='Имя', 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_name'
        })
    )
    patronymic = forms.CharField(
        label='Отчество',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_patronymic'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_email'
        })
    )
    rules = forms.BooleanField(
        label='Согласен с правилами регистрации',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_rules'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['surname', 'name', 'patronymic', 'username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Логин',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переименовываем стандартные поля
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'id': 'id_password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'id': 'id_password2'
        })

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        if surname and not re.match(r'^[а-яА-ЯёЁ\s-]+$', surname):
            raise forms.ValidationError('Фамилия может содержать только кириллицу, пробелы и тире')
        return surname

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and not re.match(r'^[а-яА-ЯёЁ\s-]+$', name):
            raise forms.ValidationError('Имя может содержать только кириллицу, пробелы и тире')
        return name

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic')
        if patronymic and not re.match(r'^[а-яА-ЯёЁ\s-]+$', patronymic):
            raise forms.ValidationError('Отчество может содержать только кириллицу, пробелы и тире')
        return patronymic

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not re.match(r'^[a-zA-Z0-9-]+$', username):
            raise forms.ValidationError('Логин может содержать только латиницу, цифры и тире')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Пароли не совпадают")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.last_name = self.cleaned_data['surname']
        user.first_name = self.cleaned_data['name']
        user.patronymic = self.cleaned_data['patronymic']
        
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',  
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_username'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password'
        })
    )

class OrderConfirmationForm(forms.Form):
    password = forms.CharField(
        label='Пароль для подтверждения заказа',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.user and not self.user.check_password(password):
            raise ValidationError('Неверный пароль')
        return password