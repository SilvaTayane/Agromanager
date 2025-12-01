from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Categoria, Item, MovimentacaoEstoque

class CategoriaModelTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Eletrônicos")
    
    def test_criacao_categoria(self):
        """Testa a criação de uma categoria"""
        self.assertEqual(self.categoria.nome, "Eletrônicos")
    
    def test_string_representation(self):
        """Testa o método __str__ da categoria"""
        self.assertEqual(str(self.categoria), "Eletrônicos")

class ItemModelTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Eletrônicos")
        self.item = Item.objects.create(
            nome="Notebook",
            categoria=self.categoria,
            quantidade_atual=10,
            quantidade_minima=5,
            quantidade_maxima=100
        )
    
    def test_criacao_item(self):
        """Testa a criação de um item"""
        self.assertEqual(self.item.nome, "Notebook")
        self.assertEqual(self.item.categoria.nome, "Eletrônicos")
        self.assertEqual(self.item.quantidade_atual, 10)
        self.assertTrue(self.item.status)
    
    def test_valores_padrao_item(self):
        """Testa os valores padrão do item"""
        self.assertEqual(self.item.unidade_medida, 'un')
        self.assertEqual(self.item.quantidade_minima, 5)
        self.assertEqual(self.item.quantidade_maxima, 100)
        self.assertTrue(self.item.status)
    
    def test_string_representation_item(self):
        """Testa o método __str__ do item"""
        self.assertEqual(str(self.item), "Notebook")

class MovimentacaoEstoqueModelTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Eletrônicos")
        self.item = Item.objects.create(
            nome="Notebook",
            categoria=self.categoria,
            quantidade_atual=10
        )
        self.movimentacao = MovimentacaoEstoque.objects.create(
            tipo_movimentacao='entrada',
            item=self.item,
            quantidade_movimentada=5,
            usuario_responsavel="admin"
        )
    
    def test_criacao_movimentacao(self):
        """Testa a criação de uma movimentação"""
        self.assertEqual(self.movimentacao.tipo_movimentacao, 'entrada')
        self.assertEqual(self.movimentacao.item.nome, "Notebook")
        self.assertEqual(self.movimentacao.quantidade_movimentada, 5)
        self.assertEqual(self.movimentacao.usuario_responsavel, "admin")
    
    def test_string_representation_movimentacao(self):
        """Testa o método __str__ da movimentação"""
        expected = "entrada - Notebook"
        self.assertEqual(str(self.movimentacao), expected)

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nome="Eletrônicos")
        self.item = Item.objects.create(
            nome="Notebook",
            categoria=self.categoria,
            quantidade_atual=10
        )
    
    def test_listar_estoque_view(self):
        """Testa a view de listar estoque"""
        response = self.client.get(reverse('listar_estoque'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listar_items.html')
        self.assertContains(response, "Notebook")
    
    def test_visualizar_item_view(self):
        """Testa a view de visualizar item"""
        response = self.client.get(reverse('visualizar_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visualizar_item.html')
        self.assertContains(response, self.item.nome)
    
    def test_criar_item_view_get(self):
        """Testa o GET da view de criar item"""
        response = self.client.get(reverse('criar_item'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'criar_item.html')
    
    def test_editar_item_view_get(self):
        """Testa o GET da view de editar item"""
        response = self.client.get(reverse('editar_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editar_item.html')
    
    def test_excluir_item_view_get(self):
        """Testa o GET da view de excluir item"""
        response = self.client.get(reverse('excluir_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'excluir_item.html')
    
    def test_historico_movimentacoes_view(self):
        """Testa a view de histórico de movimentações"""
        response = self.client.get(reverse('historico_movimentacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historico_movimentacoes.html')

class MovimentacaoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nome="Eletrônicos")
        self.item = Item.objects.create(
            nome="Notebook",
            categoria=self.categoria,
            quantidade_atual=10
        )
    
    def test_registrar_movimentacao_view_get(self):
        """Testa o GET da view de registrar movimentação"""
        response = self.client.get(reverse('registrar_movimentacao'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registrar_movimentacao.html')
    
    def test_registrar_entrada_estoque(self):
        """Testa registrar uma entrada no estoque"""
        data = {
            'tipo_movimentacao': 'entrada',
            'item': self.item.id,
            'quantidade_movimentada': 5,
            'usuario_responsavel': 'test_user'
        }
        response = self.client.post(reverse('registrar_movimentacao'), data)
        
        # Verifica se redirecionou corretamente
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a quantidade foi atualizada
        item_atualizado = Item.objects.get(id=self.item.id)
        self.assertEqual(item_atualizado.quantidade_atual, 15)
        
        # Verifica se a movimentação foi criada
        movimentacao = MovimentacaoEstoque.objects.first()
        self.assertEqual(movimentacao.tipo_movimentacao, 'entrada')
        self.assertEqual(movimentacao.quantidade_movimentada, 5)
    
    def test_registrar_saida_estoque_sucesso(self):
        """Testa registrar uma saída no estoque com estoque suficiente"""
        data = {
            'tipo_movimentacao': 'saida',
            'item': self.item.id,
            'quantidade_movimentada': 3,
            'usuario_responsavel': 'test_user'
        }
        response = self.client.post(reverse('registrar_movimentacao'), data)
        
        # Verifica se redirecionou corretamente
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a quantidade foi atualizada
        item_atualizado = Item.objects.get(id=self.item.id)
        self.assertEqual(item_atualizado.quantidade_atual, 7)
    
    def test_registrar_saida_estoque_insuficiente(self):
        """Testa registrar uma saída no estoque com estoque insuficiente"""
        data = {
            'tipo_movimentacao': 'saida',
            'item': self.item.id,
            'quantidade_movimentada': 15,  # Mais do que tem em estoque
            'usuario_responsavel': 'test_user'
        }
        response = self.client.post(reverse('registrar_movimentacao'), data)
        
        # Verifica que não redireciona (fica na mesma página com erro)
        self.assertEqual(response.status_code, 200)
        
        # Verifica que a quantidade NÃO foi alterada
        item_atualizado = Item.objects.get(id=self.item.id)
        self.assertEqual(item_atualizado.quantidade_atual, 10)
        
        # Verifica que a mensagem de erro está presente
        self.assertContains(response, "Estoque insuficiente")