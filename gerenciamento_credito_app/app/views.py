from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Contrato
from rest_framework.permissions import IsAuthenticated
from .serializers import ContratoSerializer
from django.db.models import Sum, Avg
from rest_framework import status


class ContratoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer

    # Filtros para consulta de contratos
    def get_queryset(self):
        queryset = Contrato.objects.all()

        # Filtro por ID
        contrato_id = self.request.query_params.get('id')
        if contrato_id:
            queryset = queryset.filter(id=contrato_id)

        # Filtro por CPF
        cpf = self.request.query_params.get('cpf')
        if cpf:
            queryset = queryset.filter(numero_documento=cpf)

        # Filtro por Data de Emissão
        data_emissao = self.request.query_params.get('data_emissao')
        if data_emissao:
            queryset = queryset.filter(data_emissao=data_emissao)

        # Filtro por Estado
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(endereco_tomador__contains={'estado': estado})

        return queryset


    # Resumo dos contratos
    @action(detail=False, methods=['get'])
    def resumo(self, request):
        # Filtros aplicáveis
        cpf = request.query_params.get('cpf')
        data_emissao = request.query_params.get('data_emissao')
        estado = request.query_params.get('estado')

        queryset = Contrato.objects.all()

        if cpf:
            queryset = queryset.filter(numero_documento=cpf)
        if data_emissao:
            queryset = queryset.filter(data_emissao=data_emissao)
        if estado:
            queryset = queryset.filter(endereco_tomador__contains={'estado': estado})

        total_valor_parcelas = queryset.aggregate(Sum('parcelas__valor_parcela'))['parcelas__valor_parcela__sum'] or 0
        total_valor_desembolsado = queryset.aggregate(Sum('valor_desembolsado'))['valor_desembolsado__sum'] or 0
        num_contratos = queryset.count()
        taxa_media = queryset.aggregate(Avg('taxa_contrato'))['taxa_contrato__avg'] or 0

        resumo = {
            "valor_total_a_receber": total_valor_parcelas,
            "valor_total_desembolsado": total_valor_desembolsado,
            "numero_total_de_contratos": num_contratos,
            "taxa_media_dos_contratos": taxa_media,
        }

        return Response(resumo, status=status.HTTP_200_OK)