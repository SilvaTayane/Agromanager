from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, Mock
from .models import RegistroClimatico
from .views import WEATHERCODES
import datetime

class RegistroClimaticoModelTest(TestCase):
    def setUp(self):
        self.registro = RegistroClimatico.objects.create(
            temperatura=25.5,
            umidade=70.0,
            vento=15.0,
            condicao=1,
            origem="API"
        )
    
    def test_criacao_registro_climatico(self):
        """Testa a criação de um registro climático"""
        self.assertEqual(self.registro.temperatura, 25.5)
        self.assertEqual(self.registro.umidade, 70.0)
        self.assertEqual(self.registro.vento, 15.0)
        self.assertEqual(self.registro.condicao, 1)
        self.assertEqual(self.registro.origem, "API")
    
    def test_valores_padrao(self):
        """Testa os valores padrão do registro climático"""
        registro_padrao = RegistroClimatico.objects.create(
            temperatura=20.0,
            condicao=0
        )
        self.assertEqual(registro_padrao.origem, "API")
        self.assertIsNotNone(registro_padrao.data_coleta)
        self.assertIsNotNone(registro_padrao.criado_em)
        self.assertIsNotNone(registro_padrao.atualizado_em)
    
    def test_string_representation(self):
        """Testa o método __str__ do registro climático"""
        expected = f"{self.registro.data_coleta} - {self.registro.temperatura}°C"
        self.assertEqual(str(self.registro), expected)

class WeatherCodesTest(TestCase):
    def test_weathercodes_dict(self):
        """Testa se o dicionário de weather codes está completo"""
        self.assertIn(0, WEATHERCODES)
        self.assertIn(95, WEATHERCODES)
        self.assertEqual(WEATHERCODES[0], "Céu limpo")
        self.assertEqual(WEATHERCODES[95], "Tempestade")

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria alguns registros de teste
        self.registro1 = RegistroClimatico.objects.create(
            temperatura=22.0,
            condicao=1,
            origem="API",
            data_coleta=timezone.now() - datetime.timedelta(days=1)
        )
        self.registro2 = RegistroClimatico.objects.create(
            temperatura=24.0,
            condicao=3,
            origem="API",
            data_coleta=timezone.now()
        )
    
    def test_monitoramento_view(self):
        """Testa a view monitoramento (clima_atual)"""
        response = self.client.get(reverse('monitoramento'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitoramento.html')
    
    @patch('apps.monitoramento.views.requests.get')
    def test_clima_atual_view_success(self, mock_get):
        """Testa a view clima_atual com sucesso na API"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 25.5,
                "wind_speed_10m": 12.0,
                "wind_direction_10m": 180,
                "weather_code": 1
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = self.client.get(reverse('monitoramento'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitoramento.html')
        self.assertEqual(response.context['temperatura'], 25.5)
        self.assertEqual(response.context['vento'], 12.0)
        self.assertEqual(response.context['condicao_texto'], "Poucas nuvens")
    
    @patch('apps.monitoramento.views.requests.get')
    def test_clima_atual_view_api_error(self, mock_get):
        """Testa a view clima_atual com erro na API"""
        mock_get.side_effect = Exception("Erro de conexão")
        
        response = self.client.get(reverse('monitoramento'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitoramento.html')
        self.assertIn('erro', response.context)
        self.assertContains(response, "Erro ao consultar API")
    
    @patch('apps.monitoramento.views.requests.get')
    def test_clima_atual_view_empty_data(self, mock_get):
        """Testa a view clima_atual com dados vazios da API"""
        mock_response = Mock()
        mock_response.json.return_value = {"current": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = self.client.get(reverse('monitoramento'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('erro', response.context)
        self.assertContains(response, "A API não retornou dados climáticos")
    
    def test_historico_semanal_view(self):
        """Testa a view historico_semanal"""
        response = self.client.get(reverse('historico_clima_semanal'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historico_climatico_semanal.html')
        self.assertIn('registros', response.context)
        self.assertIn('medias_por_dia', response.context)
        
        # Verifica se os registros estão no contexto
        registros = response.context['registros']
        self.assertEqual(registros.count(), 2)
    
    def test_historico_mensal_view(self):
        """Testa a view historico_mensal"""
        response = self.client.get(reverse('historico_clima_mensal'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historico_climatico_mensal.html')
        self.assertIn('registros', response.context)
        self.assertIn('medias_por_dia', response.context)
        
        registros = response.context['registros']
        self.assertEqual(registros.count(), 2)
    
    @patch('apps.monitoramento.views.requests.get')
    def test_previsao_view_success(self, mock_get):
        """Testa a view previsao com sucesso"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "daily": {
                "temperature_2m_max": [28, 29, 30],
                "temperature_2m_min": [18, 19, 20],
                "precipitation_probability_max": [10, 20, 30]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = self.client.get(reverse('previsao_semana'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'previsao.html')
        self.assertIn('previsao', response.context)
        self.assertIsNotNone(response.context['previsao'])
    
    @patch('apps.monitoramento.views.requests.get')
    def test_previsao_view_error(self, mock_get):
        """Testa a view previsao com erro"""
        mock_get.side_effect = Exception("Timeout")
        
        response = self.client.get(reverse('previsao_semana'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'previsao.html')
        self.assertIn('previsao', response.context)

class RegistroClimaticoManagerTest(TestCase):
    def setUp(self):
        # Cria registros com datas diferentes
        hoje = timezone.now()
        self.registro_hoje = RegistroClimatico.objects.create(
            temperatura=25.0,
            condicao=0,
            data_coleta=hoje
        )
        self.registro_ontem = RegistroClimatico.objects.create(
            temperatura=23.0,
            condicao=1,
            data_coleta=hoje - datetime.timedelta(days=1)
        )
        self.registro_semana_passada = RegistroClimatico.objects.create(
            temperatura=20.0,
            condicao=3,
            data_coleta=hoje - datetime.timedelta(days=8)
        )
    
    def test_filtro_por_periodo(self):
        """Testa filtros por período temporal"""
        # Testa filtro dos últimos 7 dias
        hoje = timezone.now().date()
        inicio_semana = hoje - datetime.timedelta(days=7)
        
        registros_semana = RegistroClimatico.objects.filter(
            data_coleta__date__gte=inicio_semana
        )
        
        self.assertEqual(registros_semana.count(), 2)  # hoje e ontem
    
    def test_ordenacao(self):
        """Testa a ordenação dos registros"""
        registros_ordenados = RegistroClimatico.objects.order_by('-data_coleta')
        self.assertEqual(registros_ordenados.first(), self.registro_hoje)
        self.assertEqual(registros_ordenados.last(), self.registro_semana_passada)

# Testes para verificar templates (opcional)
class TemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.registro = RegistroClimatico.objects.create(
            temperatura=25.5,
            condicao=1,
            origem="API"
        )
    
    def test_monitoramento_template_content(self):
        """Testa se o template de monitoramento renderiza corretamente"""
        response = self.client.get(reverse('monitoramento'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitoramento.html')