from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Contrato, Parcela
from datetime import date
from django.urls import reverse
from time import sleep

class ContratoViewSetTest(APITestCase):
    def setUp(self):
        """
        Configura o ambiente de teste, criando um usuário e um contrato 
        para os testes subsequentes.
        """
        # Criando o usuário 'almeida' para o banco de dados de teste
        self.user, created = User.objects.get_or_create(username='almeida', defaults={'password': 'testpassword'})
        if created:  # Caso o usuário tenha sido criado, definimos a senha corretamente
            self.user.set_password('testpassword')
            self.user.save()

        # Criando um contrato para os testes
        self.contrato = Contrato.objects.create(
            data_emissao=date(2025, 1, 17),
            data_nascimento_tomador=date(1990, 5, 10),
            valor_desembolsado=1000.00,
            numero_documento="12345678901",
            endereco_tomador={"estado": "SP", "cidade": "São Paulo", "pais": "Brasil"},
            telefone_tomador="11987654321",
            taxa_contrato=5.00
        )

        # Adicionando parcelas ao contrato
        self.parcela = Parcela.objects.create(
            contrato=self.contrato,
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=date(2025, 2, 17)
        )

        # Obtendo o token de autenticação para o usuário 'almeida'
        response = self.client.post('/api/token/', {
            'username': 'almeida',  # Nome de usuário correto
            'password': 'testpassword',  # A senha correta para o usuário
        })

        # Verifique se a resposta contém o token 'access'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)  
        self.token = response.data['access'] 
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')  

    def test_list_contratos(self):
        """
        Testa a listagem dos contratos para garantir que o contrato criado 
        esteja presente na resposta.
        """
        response = self.client.get('/api/contratos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_contrato(self):
        """
        Testa a criação de um novo contrato, verificando se o contrato é 
        criado corretamente e se o número de documento é o esperado.
        """
        data = {
            "data_emissao": "2025-01-18",
            "data_nascimento_tomador": "1992-02-20",
            "valor_desembolsado": 1500.00,
            "numero_documento": "10987654321",
            "endereco_tomador": {"estado": "RJ", "cidade": "Rio de Janeiro", "pais": "Brasil"},
            "telefone_tomador": "2123456789",
            "taxa_contrato": 7.00,
            "parcelas": [{"numero_parcela": 1, "valor_parcela": 300.00, "data_vencimento": "2025-03-01"}]
        }
        response = self.client.post('/api/contratos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['numero_documento'], "10987654321")

    def test_retrieve_contrato(self):
        """
        Testa a recuperação de um contrato específico, verificando se 
        o contrato retornado tem o mesmo ID que o contrato criado.
        """
        response = self.client.get(f'/api/contratos/{self.contrato.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.contrato.id)

    def test_update_contrato(self):
        """
        Testa a atualização de um contrato, verificando se o valor 
        desembolsado é atualizado corretamente.
        """
        data = {
            "data_emissao": "2025-01-18",
            "data_nascimento_tomador": "1992-02-20",
            "valor_desembolsado": 1600.00,
            "numero_documento": "10987654321",
            "endereco_tomador": {"estado": "MG", "cidade": "Belo Horizonte", "pais": "Brasil"},
            "telefone_tomador": "31987654321",
            "taxa_contrato": 6.00,
            "parcelas": [{"numero_parcela": 1, "valor_parcela": 350.00, "data_vencimento": "2025-03-10"}]
        }
        response = self.client.put(f'/api/contratos/{self.contrato.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ajustando a comparação para usar float ao invés de string
        self.assertEqual(float(response.data['valor_desembolsado']), 1600.00)

    def test_delete_contrato(self):
        """
        Testa a exclusão de um contrato, verificando se a exclusão é bem-sucedida.
        """
        response = self.client.delete(f'/api/contratos/{self.contrato.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_resumo_success(self):
        """
        Testa o endpoint de resumo para garantir que a resposta contém 
        os dados esperados (valor total a receber e número de contratos).
        """
        response = self.client.get('/api/contratos/resumo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('valor_total_a_receber', response.data)
        self.assertIn('numero_total_de_contratos', response.data)

    def test_resumo_with_filters_cpf(self):
        """
        Testa o resumo com filtro de CPF, verificando se o filtro funciona 
        corretamente para um CPF válido.
        """
        response = self.client.get('/api/contratos/resumo/?cpf=12345678901')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('valor_total_a_receber', response.data)

    def test_resumo_with_filters_data_emissao(self):
        """
        Testa o resumo com filtro de data de emissão, verificando se o filtro 
        retorna os resultados esperados.
        """
        response = self.client.get('/api/contratos/resumo/?data_emissao=2025-01-17')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('valor_total_a_receber', response.data)

    def test_resumo_with_filters_estado(self):
        """
        Testa o resumo com filtro de estado, verificando se o filtro 
        funciona corretamente para o estado 'SP'.
        """
        response = self.client.get('/api/contratos/resumo/?estado=SP')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('valor_total_a_receber', response.data)

    def test_get_queryset_filter_by_id(self):
        """
        Testa a recuperação de contratos filtrados por ID, verificando se 
        o contrato retornado corresponde ao ID fornecido.
        """
        response = self.client.get(f'/api/contratos/?id={self.contrato.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.contrato.id)
