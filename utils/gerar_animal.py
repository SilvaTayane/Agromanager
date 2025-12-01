import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# ------------------ CONFIGURAÇÃO DO DJANGO ------------------
# Caminho base do projeto (onde está o manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Ajusta o módulo de configurações do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agromanager.settings")

# Inicializa o Django
django.setup()
# ------------------------------------------------------------

from faker import Faker
from apps.animal.models import Animal  

fake = Faker('pt_BR')

# Nomes específicos para animais
NOMES_ANIMAIS = {
    "Bovino": ["Boi", "Vaca", "Bezerro", "Bezerra", "Novilho", "Novilha", "Touro"],
    "Suíno": ["Porco", "Porca", "Leitão", "Leitoa", "Marrano", "Cachaço"],
    "Caprino": ["Bode", "Cabra", "Cabrito", "Cabrita"],
    "Ovino": ["Carneiro", "Ovelha", "Cordeiro", "Cordeira"],
    "Equino": ["Cavalo", "Égua", "Potro", "Potra", "Jumento", "Jumenta"],
    "Aves": ["Galinha", "Galo", "Pinto", "Pinta", "Frango", "Pata", "Pato"]
}

RACAS = {
    "Bovino": ["Nelore", "Angus", "Hereford", "Brahman", "Girolando", "Holandês"],
    "Suíno": ["Landrace", "Large White", "Duroc", "Pietrain"],
    "Caprino": ["Saanen", "Alpina", "Angorá", "Boer"],
    "Ovino": ["Dorper", "Suffolk", "Merino", "Santa Inês"],
    "Equino": ["Quarto de Milha", "Mangalarga", "Árabe", "Crioulo"],
    "Aves": ["Rhode Island", "Sussex", "Leghorn", "Plymouth"]
}

def criar_animais(quantidade=50):
    animais_criados = []
    
    for i in range(quantidade):
        especie = random.choice(list(NOMES_ANIMAIS.keys()))
        nome = random.choice(NOMES_ANIMAIS[especie])
        raca = random.choice(RACAS[especie])

        if nome in ["Boi", "Touro", "Novilho", "Galo", "Bode", "Carneiro", "Cavalo", "Jumento", "Pato", "Bezerro", "Leitão", "Cabrito", "Cordeiro", "Potro"]:
            sexo = "Macho"
        else:
            sexo = "Fêmea"

        data_nascimento = fake.date_between(start_date='-5y', end_date='today')

        if random.random() > 0.3:
            data_aquisicao = fake.date_between(start_date=data_nascimento, end_date='today')
            origem = random.choice(["Compra", "Nascimento Interno", "Doação"])
        else:
            data_aquisicao = None
            origem = None

        if origem == "Compra":
            if especie == "Bovino":
                valor = random.uniform(800, 3000)
            elif especie == "Equino":
                valor = random.uniform(1500, 5000)
            elif especie in ["Suíno", "Caprino", "Ovino"]:
                valor = random.uniform(200, 800)
            else:
                valor = random.uniform(10, 50)
            valor_compra = Decimal(valor).quantize(Decimal('0.01'))
        else:
            valor_compra = Decimal('0.00')

        if especie == "Bovino" and sexo == "Fêmea":
            finalidade = random.choice(["Leite", "Reprodução"])
        elif especie == "Aves" and sexo == "Fêmea":
            finalidade = random.choice(["Reprodução", "Venda"])
        elif especie in ["Suíno", "Aves"]:
            finalidade = random.choice(["Corte", "Reprodução"])
        else:
            finalidade = random.choice(["Corte", "Reprodução", "Venda"])

        if especie == "Bovino":
            peso_inicial = Decimal(random.uniform(30, 80))
        elif especie == "Suíno":
            peso_inicial = Decimal(random.uniform(1, 5))
        elif especie in ["Caprino", "Ovino"]:
            peso_inicial = Decimal(random.uniform(2, 8))
        elif especie == "Equino":
            peso_inicial = Decimal(random.uniform(40, 100))
        else:
            peso_inicial = Decimal(random.uniform(0.1, 0.5))
        peso_inicial = peso_inicial.quantize(Decimal('0.01'))

        numero_identificacao = f"{especie[:3].upper()}{fake.random_number(digits=6, fix_len=True)}"

        animal = Animal(
            nome=nome,
            especie=especie,
            raca=raca,
            sexo=sexo,
            data_nascimento=data_nascimento,
            numero_identificacao=numero_identificacao,
            finalidade=finalidade,
            peso_inicial=peso_inicial,
            observacoes=fake.text(max_nb_chars=100) if random.random() > 0.7 else "",
            data_aquisicao=data_aquisicao,
            origem=origem,
            valor_compra=valor_compra,
            criado_por=fake.first_name()
        )

        animal.save()
        animais_criados.append(animal)

        if (i + 1) % 10 == 0:
            print(f"Criados {i + 1} animais...")

    return animais_criados


if __name__ == "__main__":
    print("🐄 Populando banco de dados com animais...")
    animais = criar_animais(50)
    print(f"✅ {len(animais)} animais criados com sucesso!")
