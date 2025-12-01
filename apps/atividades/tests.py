from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Atividade, LogAtividade


# ---------------------------------------------------------
# TESTES DO MANAGER
# ---------------------------------------------------------
class AtividadeManagerTest(TestCase):
    def test_manager_ativas(self):
        ativa = Atividade.objects.create(titulo="A", nome_trabalhador="Gustavo")
        excluida = Atividade.objects.create(
            titulo="B",
            nome_trabalhador="Gustavo",
            data_exclusao=timezone.now()
        )

        qs = Atividade.objects.ativas()

        self.assertEqual(qs.count(), 1)
        self.assertIn(ativa, qs)
        self.assertNotIn(excluida, qs)


# ---------------------------------------------------------
# TESTES DO MODEL
# ---------------------------------------------------------
class AtividadeModelTest(TestCase):
    def test_criacao_basica(self):
        a = Atividade.objects.create(titulo="Teste")
        self.assertEqual(a.titulo, "Teste")
        self.assertIsNone(a.data_exclusao)

    def test_valores_padrao(self):
        a = Atividade.objects.create(titulo="Teste")
        self.assertEqual(a.prioridade, "MEDIA")
        self.assertEqual(a.tipo_atividade, "GERAL")
        self.assertEqual(a.status, "registrada")

    def test_metodo_excluir_logicamente(self):
        a = Atividade.objects.create(titulo="Teste")
        a.excluir_logicamente("admin")

        self.assertIsNotNone(a.data_exclusao)
        self.assertEqual(a.usuario_responsavel, "admin")
        self.assertEqual(a.logs.count(), 1)

    def test_esta_atrasada(self):
        a = Atividade.objects.create(
            titulo="Atrasada",
            data_limite=timezone.now() - timezone.timedelta(days=1)
        )
        self.assertTrue(a.esta_atrasada())


# ---------------------------------------------------------
# TESTES DE VIEW
# ---------------------------------------------------------
class AtividadeViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.atividade = Atividade.objects.create(
            titulo="A1",
            nome_trabalhador="Gustavo",
            data_limite=timezone.now() + timezone.timedelta(days=1)
        )

    # -----------------------------
    def test_menuativ_view(self):
        resp = self.client.get(reverse("menu_atividades"))
        self.assertEqual(resp.status_code, 200)

    # -----------------------------
    def test_listar_atividades_admin(self):
        resp = self.client.get(reverse("listar_atividades_admin"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("atividades", resp.context)

    # -----------------------------
    def test_criar_atividade_post(self):
        resp = self.client.post(reverse("criar_atividade"), {
            "titulo": "Teste POST",
            "tipo_atividade": "GERAL",
            "prioridade": "MEDIA",
            "descricao": "xx"
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Atividade.objects.count(), 2)
        self.assertEqual(LogAtividade.objects.count(), 1)

    # -----------------------------
    def test_editar_atividade_post(self):
        resp = self.client.post(
            reverse("editar_atividade", args=[self.atividade.id_atividade]),
            {
                "titulo": "Editado",
                "tipo_atividade": "AGRICOLA",
                "prioridade": "ALTA",
                "status": "registrada"
            }
        )
        self.assertEqual(resp.status_code, 302)

        self.atividade.refresh_from_db()
        self.assertEqual(self.atividade.titulo, "Editado")
        self.assertEqual(LogAtividade.objects.count(), 1)

    # -----------------------------
    def test_excluir_atividade_post(self):
        resp = self.client.post(
            reverse("excluir_atividade", args=[self.atividade.id_atividade])
        )
        self.assertEqual(resp.status_code, 302)

        self.atividade.refresh_from_db()
        self.assertIsNotNone(self.atividade.data_exclusao)
        self.assertEqual(LogAtividade.objects.count(), 1)

    # -----------------------------
    def test_atualizar_status_post(self):
        atividade = self.atividade

        resp = self.client.post(
            reverse("atualizar_status", args=[atividade.id_atividade, atividade.nome_trabalhador]),
            {
                "status": "com_problemas",
                "descricao_problema": "Pane"
            }
        )

        self.assertEqual(resp.status_code, 302)

        atividade.refresh_from_db()
        self.assertEqual(atividade.status, "com_problemas")
        self.assertEqual(atividade.descricao_problema, "Pane")
        self.assertEqual(LogAtividade.objects.count(), 1)
