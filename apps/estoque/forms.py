from django import forms
from .models import Item, MovimentacaoEstoque

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'nome', 
            'categoria', 
            'unidade_medida',     
            'quantidade_atual', 
            'quantidade_minima',  
            'quantidade_maxima',  
            'localizacao',        
            'status',            
            'descricao'
        ]
        
        
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ['item', 'tipo_movimentacao', 'quantidade_movimentada', 'usuario_responsavel']