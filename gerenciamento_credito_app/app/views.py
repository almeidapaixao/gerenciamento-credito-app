from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Contrato
from rest_framework.permissions import IsAuthenticated
from .serializers import ContratoSerializer
from django.db.models import Sum, Avg
from rest_framework import status
from django.views.decorators.gzip import gzip_page
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import timedelta


class ContratoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer

    # Filtros para consulta de contratos
    def get_queryset(self):
        """
        Retorna o queryset filtrado com base nos parâmetros de consulta fornecidos na requisição.
        Filtros disponíveis:
        - id: Filtra contratos pelo ID.
        - cpf: Filtra contratos pelo número do documento (CPF).
        - data_emissao: Filtra contratos pela data de emissão.
        - estado: Filtra contratos pelo estado do endereço do tomador.
        Retorna:
            QuerySet: O queryset filtrado de acordo com os parâmetros fornecidos.
            
        Como prefiro simplicidade do que complexido, uso ifs encadeados mas tambem
        posso implementar solucoes mais complexas
        """
        queryset = Contrato.objects.all()

        contrato_id = self.request.query_params.get('id')
        if contrato_id:
            queryset = queryset.filter(id=contrato_id)

        cpf = self.request.query_params.get('cpf')
        if cpf:
            queryset = queryset.filter(numero_documento=cpf)

        data_emissao = self.request.query_params.get('data_emissao')
        if data_emissao:
            queryset = queryset.filter(data_emissao=data_emissao)

        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(Q(endereco_tomador__estado=estado))

        return queryset

    @gzip_page
    @action(detail=False, methods=['get'])
    def resumo(self, request):
        """
        Retorna um resumo dos contratos filtrados por CPF, data de emissão e estado.
        Este endpoint permite aplicar filtros opcionais para CPF, data de emissão e estado,
        e retorna um resumo contendo o valor total a receber, valor total desembolsado,
        número total de contratos e a taxa média dos contratos.
        Parâmetros:
        - request: Objeto HttpRequest que pode conter os seguintes parâmetros de consulta:
            - cpf: CPF do tomador do contrato.
            - data_emissao: Data de emissão do contrato.
            - estado: Estado do endereço do tomador do contrato.
        Retorna:
        - Response: Um objeto Response contendo um dicionário com os seguintes dados:
            - valor_total_a_receber: Soma total dos valores das parcelas dos contratos filtrados.
            - valor_total_desembolsado: Soma total dos valores desembolsados dos contratos filtrados.
            - numero_total_de_contratos: Número total de contratos filtrados.
            - taxa_media_dos_contratos: Taxa média dos contratos filtrados.
    """
        cpf = request.query_params.get('cpf')
        data_emissao = request.query_params.get('data_emissao')
        estado = request.query_params.get('estado')

        queryset = Contrato.objects.all()

        if cpf:
            queryset = queryset.filter(numero_documento=cpf)
        if data_emissao:
            queryset = queryset.filter(data_emissao=data_emissao)
        if estado:
            queryset = queryset.filter(Q(endereco_tomador__estado=estado))

        total_valor_parcelas = queryset.aggregate(Sum('parcelas__valor_parcela'))['parcelas__valor_parcela__sum'] or 0
        total_valor_desembolsado = queryset.aggregate(Sum('valor_desembolsado'))['valor_desembolsado__sum'] or 0
        num_contratos = queryset.count()
        taxa_media = queryset.aggregate(Avg('taxa_contrato'))['taxa_contrato__avg'] or 0

        if total_valor_parcelas == 0 and total_valor_desembolsado == 0 and num_contratos == 0 and taxa_media == 0:
            resumo = []
        else:
            resumo = {
            "valor_total_a_receber": total_valor_parcelas,
            "valor_total_desembolsado": total_valor_desembolsado,
            "numero_total_de_contratos": num_contratos,
            "taxa_media_dos_contratos": taxa_media,
            }

        return Response(resumo, status=status.HTTP_200_OK)


class TokenObtainFor30DaysView(APIView):
    """
    TokenObtainFor30DaysView é uma APIView que permite a obtenção de um token de acesso com validade de 30 dias.
    Permissões:
        - IsAuthenticated: Apenas usuários autenticados podem acessar esta view.
    Métodos:
        - post(request): Gera e retorna um token de acesso e um token de atualização para o usuário autenticado. O token de acesso tem uma validade de 30 dias.
    Parâmetros:
        - request: Objeto HttpRequest que contém os dados da requisição.
    Retorno:
        - Response: Retorna uma resposta HTTP 200 OK contendo o token de acesso e o token de atualização.
        
    Basta solicitar um novo codigo neste view para obter um novo token durante 30 dias.
    """
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        refresh = RefreshToken.for_user(request.user)
        access_token = refresh.access_token

        access_token.set_exp(lifetime=timedelta(days=30))

        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
