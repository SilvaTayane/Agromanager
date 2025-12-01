from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Page
from django.contrib.messages import get_messages
from .models import Animal
from .forms import AnimalForm
import datetime

class AnimalModelTest(TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            nome="Boi Veloz",
            especie="Bovino",
            raca="Nelore",
            sexo="Macho",
            data_nascimento="2022-05-15",
            numero_identificacao="NV001",
            finalidade="Corte",
            peso_inicial=250.50,
            origem="Compra",
            data_aquisicao="2022-05-20",
            valor_compra=1500.00
        )
    
    def test_criacao_animal(self):
        """Testa a criação de um animal"""
        self.assertEqual(self.animal.nome, "Boi Veloz")
        self.assertEqual(self.animal.especie, "Bovino")
        self.assertEqual(self.animal.raca, "Nelore")
        self.assertEqual(self.animal.sexo, "Macho")
        self.assertEqual(self.animal.finalidade, "Corte")
        self.assertEqual(self.animal.peso_inicial, 250.50)
        self.assertEqual(self.animal.origem, "Compra")
        self.assertEqual(self.animal.valor_compra, 1500.00)
    
    def test_valores_padrao(self):
        """Testa os valores padrão do animal"""
        animal_padrao = Animal.objects.create(
            nome="Vaca Leiteira",
            especie="Bovino",
            sexo="Fêmea",
            data_nascimento="2021-03-10"
        )
        self.assertEqual(animal_padrao.valor_compra, 0.00)
        self.assertIsNotNone(animal_padrao.data_criacao)
    
    def test_string_representation(self):
        """Testa o método __str__ do animal"""
        expected = f"{self.animal.id} - Boi Veloz - Bovino"
        self.assertEqual(str(self.animal), expected)
    
    def test_meta_attributes(self):
        """Testa os atributos Meta do modelo"""
        self.assertEqual(Animal._meta.verbose_name, "Animal")
        self.assertEqual(Animal._meta.verbose_name_plural, "Animais")
        self.assertEqual(Animal._meta.ordering, ['-id'])
    
    def test_numero_identificacao_unico(self):
        """Testa que número de identificação deve ser único"""
        with self.assertRaises(Exception):
            Animal.objects.create(
                nome="Outro Animal",
                especie="Bovino",
                sexo="Fêmea",
                data_nascimento="2020-01-01",
                numero_identificacao="NV001"
            )

class AnimalViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.animal1 = Animal.objects.create(
            nome="Boi Veloz",
            especie="Bovino",
            sexo="Macho",
            data_nascimento="2022-05-15",
            numero_identificacao="NV001",
            finalidade="Corte",
            origem="Nascimento Interno",
            valor_compra=0.00  # Adicionado valor_compra
        )
        self.animal2 = Animal.objects.create(
            nome="Vaca Leiteira",
            especie="Bovino",
            sexo="Fêmea",
            data_nascimento="2021-03-10",
            numero_identificacao="NV002",
            finalidade="Leite",
            origem="Nascimento Interno",
            valor_compra=0.00  # Adicionado valor_compra
        )
        self.animal3 = Animal.objects.create(
            nome="Porco Barriga",
            especie="Suíno",
            sexo="Macho",
            data_nascimento="2023-01-20",
            numero_identificacao="NV003",
            finalidade="Corte",
            origem="Nascimento Interno",
            valor_compra=0.00  # Adicionado valor_compra
        )
    
    def test_listar_animais_view(self):
        """Testa a view de listar animais"""
        response = self.client.get(reverse('listar_animais'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listar_animais.html')
        self.assertIn('animais', response.context)
        self.assertIn('total_animais', response.context)
        self.assertEqual(response.context['total_animais'], 3)
    
    def test_listar_animais_com_filtro_search(self):
        """Testa a listagem com filtro de busca"""
        response = self.client.get(reverse('listar_animais') + '?search=Veloz')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['animais']), 1)
        self.assertEqual(response.context['animais'][0].nome, "Boi Veloz")
    
    def test_listar_animais_com_filtro_especie(self):
        """Testa a listagem com filtro de espécie"""
        response = self.client.get(reverse('listar_animais') + '?especie=Suíno')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['animais']), 1)
        self.assertEqual(response.context['animais'][0].especie, "Suíno")
    
    def test_listar_animais_com_filtro_sexo(self):
        """Testa a listagem com filtro de sexo"""
        response = self.client.get(reverse('listar_animais') + '?sexo=Fêmea')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['animais']), 1)
        self.assertEqual(response.context['animais'][0].sexo, "Fêmea")
    
    def test_listar_animais_paginacao(self):
        """Testa a paginação na listagem de animais"""
        for i in range(15):
            Animal.objects.create(
                nome=f"Animal {i}",
                especie="Bovino",
                sexo="Macho",
                data_nascimento="2022-01-01",
                numero_identificacao=f"TEST{i}",
                origem="Nascimento Interno",
                valor_compra=0.00  # Adicionado valor_compra
            )
        
        response = self.client.get(reverse('listar_animais'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertTrue(response.context['is_paginated'])
    
    def test_detalhe_animal_view(self):
        """Testa a view de detalhe do animal"""
        response = self.client.get(reverse('detalhe_animal', args=[self.animal1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detalhe_animal.html')
        self.assertIn('animal', response.context)
        self.assertEqual(response.context['animal'], self.animal1)
        self.assertIn('health_history', response.context)
        self.assertIn('movement_history', response.context)
    
    def test_detalhe_animal_nao_existente(self):
        """Testa acesso a detalhe de animal não existente"""
        response = self.client.get(reverse('detalhe_animal', args=[999]))
        self.assertEqual(response.status_code, 404)
    
    def test_criar_animais_view_get(self):
        """Testa o GET da view de criar animal"""
        response = self.client.get(reverse('criar_animais'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'criar_animais.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], AnimalForm)
    
    def test_criar_animais_view_post_valido_nascimento_interno(self):
        """Testa o POST da view de criar animal com origem 'Nascimento Interno'"""
        data = {
            'nome': 'Novo Animal',
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-06-01',
            'numero_identificacao': 'NV999',
            'finalidade': 'Reprodução',
            'origem': 'Nascimento Interno',
            'valor_compra': '0.00'  # Campo obrigatório adicionado
        }
        
        response = self.client.post(reverse('criar_animais'), data)
        
        # Verifica redirecionamento após sucesso
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('listar_animais'))
        
        # Verifica se o animal foi criado
        self.assertTrue(Animal.objects.filter(numero_identificacao='NV999').exists())
    
    def test_criar_animais_view_post_valido_compra(self):
        """Testa o POST da view de criar animal com origem 'Compra'"""
        data = {
            'nome': 'Animal Comprado',
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-01-01',
            'numero_identificacao': 'NV888',
            'finalidade': 'Corte',
            'origem': 'Compra',
            'data_aquisicao': '2023-06-15',
            'valor_compra': '2000.00'
        }
        
        response = self.client.post(reverse('criar_animais'), data)
        
        # Verifica redirecionamento após sucesso
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('listar_animais'))
        
        # Verifica se o animal foi criado
        self.assertTrue(Animal.objects.filter(numero_identificacao='NV888').exists())
    
    def test_criar_animais_view_post_invalido(self):
        """Testa o POST da view de criar animal com dados inválidos"""
        data = {
            'nome': '',  # Nome vazio - inválido
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-06-01',
            'valor_compra': '0.00'  # Campo obrigatório adicionado
        }
        
        response = self.client.post(reverse('criar_animais'), data)
        
        # Deve permanecer na mesma página com erro
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'criar_animais.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
    
    def test_editar_animal_view_get(self):
        """Testa o GET da view de editar animal"""
        response = self.client.get(reverse('editar_animal', args=[self.animal1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'criar_animais.html')
        self.assertIn('form', response.context)
        self.assertIn('form_action', response.context)
        self.assertIsInstance(response.context['form'], AnimalForm)
    
    def test_editar_animal_view_post_valido(self):
        """Testa o POST da view de editar animal com dados válidos"""
        data = {
            'nome': 'Boi Veloz Editado',
            'especie': 'Bovino',
            'raca': 'Angus',
            'sexo': 'Macho',
            'data_nascimento': '2022-05-15',
            'numero_identificacao': 'NV001',
            'finalidade': 'Reprodução',
            'origem': 'Nascimento Interno',
            'valor_compra': '0.00'  # Campo obrigatório adicionado
        }
        
        response = self.client.post(reverse('editar_animal', args=[self.animal1.id]), data)
        
        # Verifica redirecionamento após sucesso
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('editar_animal', args=[self.animal1.id]))
        
        # Verifica se o animal foi atualizado
        animal_atualizado = Animal.objects.get(id=self.animal1.id)
        self.assertEqual(animal_atualizado.nome, 'Boi Veloz Editado')
        self.assertEqual(animal_atualizado.raca, 'Angus')
        self.assertEqual(animal_atualizado.finalidade, 'Reprodução')
    
    def test_deletar_animal_view(self):
        """Testa a view de deletar animal"""
        animal_id = self.animal1.id
        animal_nome = self.animal1.nome
        
        response = self.client.post(reverse('deletar_animal', args=[animal_id]))
        
        # Verifica redirecionamento após sucesso
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('listar_animais'))
        
        # Verifica se o animal foi deletado
        self.assertFalse(Animal.objects.filter(id=animal_id).exists())
        
        # Verifica se a mensagem de sucesso foi adicionada
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn(f'Animal "{animal_nome}" excluído com sucesso!', str(messages_list[0]))

class AnimalFormTest(TestCase):
    def test_animal_form_valido_nascimento_interno(self):
        """Testa o formulário AnimalForm com dados válidos para origem 'Nascimento Interno'"""
        form_data = {
            'nome': 'Teste Animal',
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-01-01',
            'numero_identificacao': 'TEST123',
            'finalidade': 'Corte',
            'origem': 'Nascimento Interno',
            'valor_compra': '0.00'  # Campo obrigatório adicionado
        }
        form = AnimalForm(data=form_data)
        if not form.is_valid():
            print("Erros no formulário (nascimento interno):", form.errors)
        self.assertTrue(form.is_valid())
    
    def test_animal_form_valido_compra(self):
        """Testa o formulário AnimalForm com dados válidos para origem 'Compra'"""
        form_data = {
            'nome': 'Teste Animal Comprado',
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-01-01',
            'numero_identificacao': 'TEST124',
            'finalidade': 'Corte',
            'origem': 'Compra',
            'data_aquisicao': '2023-02-01',
            'valor_compra': '1500.00'
        }
        form = AnimalForm(data=form_data)
        if not form.is_valid():
            print("Erros no formulário (compra):", form.errors)
        self.assertTrue(form.is_valid())
    
    def test_animal_form_invalido(self):
        """Testa o formulário AnimalForm com dados inválidos"""
        form_data = {
            'nome': '',  # Campo obrigatório vazio
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-01-01',
            'valor_compra': '0.00'  # Campo obrigatório adicionado
        }
        form = AnimalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
    
    def test_animal_form_campos_nao_obrigatorios(self):
        """Testa que campos não obrigatórios funcionam corretamente"""
        form_data = {
            'nome': 'Animal Simples',
            'especie': 'Bovino',
            'sexo': 'Fêmea',
            'data_nascimento': '2023-01-01',
            'origem': 'Nascimento Interno',
            'valor_compra': '0.00'  # Campo obrigatório adicionado
        }
        form = AnimalForm(data=form_data)
        if not form.is_valid():
            print("Erros no formulário (campos não obrigatórios):", form.errors)
        self.assertTrue(form.is_valid())
    
    def test_animal_form_compra_sem_data_aquisicao(self):
        """Testa que origem 'Compra' requer data_aquisicao"""
        form_data = {
            'nome': 'Animal Comprado',
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-01-01',
            'origem': 'Compra',
            'valor_compra': '1500.00'
            # data_aquisicao faltando - deve causar erro
        }
        form = AnimalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('data_aquisicao', form.errors)
    
    def test_animal_form_compra_sem_valor_compra(self):
        """Testa que origem 'Compra' requer valor_compra"""
        form_data = {
            'nome': 'Animal Comprado',
            'especie': 'Bovino',
            'sexo': 'Macho',
            'data_nascimento': '2023-01-01',
            'origem': 'Compra',
            'data_aquisicao': '2023-02-01'
            # valor_compra faltando - deve causar erro
        }
        form = AnimalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('valor_compra', form.errors)