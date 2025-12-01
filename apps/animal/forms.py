from django import forms
from .models import Animal
from django.core.exceptions import ValidationError
import datetime

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'nome',
            'numero_identificacao',
            'especie',
            'raca',
            'sexo',
            'data_nascimento',
            'peso_inicial',
            'finalidade',
            'observacoes',
            'origem',
            'data_aquisicao',
            'valor_compra',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Mimosa'
            }),
            'numero_identificacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: BV001'
            }),
            'especie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Bovino'
            }),
            'raca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Nelore'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'peso_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 450',
                'step': '0.01'
            }),
            'finalidade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Histórico médico, tratamentos, vacinas, comportamento, etc.'
            }),
            'origem': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_aquisicao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 5000.00',
                'step': '0.01'
            }),
        }
        labels = {
            'nome': 'Nome',
            'numero_identificacao': 'Número de Identificação',
            'especie': 'Espécie',
            'raca': 'Raça',
            'sexo': 'Sexo',
            'data_nascimento': 'Data de Nascimento',
            'peso_inicial': 'Peso Inicial (kg)',
            'finalidade': 'Finalidade',
            'observacoes': 'Observações',
            'origem': 'Origem',
            'data_aquisicao': 'Data de Aquisição',
            'valor_compra': 'Valor de Compra (R$)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir data máxima como hoje para os campos de data
        today = datetime.date.today().isoformat()
        self.fields['data_nascimento'].widget.attrs['max'] = today
        self.fields['data_aquisicao'].widget.attrs['max'] = today
        
        # Tornar campos obrigatórios
        self.fields['nome'].required = True
        self.fields['especie'].required = True
        self.fields['sexo'].required = True
        self.fields['data_nascimento'].required = True

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento and data_nascimento > datetime.date.today():
            raise ValidationError("A data de nascimento não pode ser futura.")
        return data_nascimento

    def clean_data_aquisicao(self):
        data_aquisicao = self.cleaned_data.get('data_aquisicao')
        if data_aquisicao and data_aquisicao > datetime.date.today():
            raise ValidationError("A data de aquisição não pode ser futura.")
        return data_aquisicao

    def clean_numero_identificacao(self):
        numero_identificacao = self.cleaned_data.get('numero_identificacao')
        
        if numero_identificacao:
            # Verificar se já existe outro animal com o mesmo número de identificação
            queryset = Animal.objects.filter(numero_identificacao=numero_identificacao)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError("Já existe um animal com este número de identificação.")
        
        return numero_identificacao

    def clean(self):
        cleaned_data = super().clean()
        data_nascimento = cleaned_data.get('data_nascimento')
        data_aquisicao = cleaned_data.get('data_aquisicao')
        origem = cleaned_data.get('origem')
        valor_compra = cleaned_data.get('valor_compra')
        
        # Validar se data de aquisição não é anterior à data de nascimento
        if data_nascimento and data_aquisicao:
            if data_aquisicao < data_nascimento:
                raise ValidationError({
                    'data_aquisicao': "A data de aquisição não pode ser anterior à data de nascimento."
                })
        
        # Validar regras para animais comprados
        if origem == 'Compra':
            if not data_aquisicao:
                raise ValidationError({
                    'data_aquisicao': "Para animais comprados, é necessário informar a data de aquisição."
                })
            if valor_compra is None or valor_compra <= 0:
                raise ValidationError({
                    'valor_compra': "Para animais comprados, é necessário informar um valor de compra válido."
                })
        
        return cleaned_data