from rest_framework import serializers
from .models import Contrato, Parcela


class ParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcela
        fields = ['numero_parcela', 'valor_parcela', 'data_vencimento']

class ContratoSerializer(serializers.ModelSerializer):
    parcelas = ParcelaSerializer(many=True)

    class Meta:
        model = Contrato
        fields = ['id', 'data_emissao', 'data_nascimento_tomador', 'valor_desembolsado', 
                  'numero_documento', 'endereco_tomador', 'telefone_tomador', 'taxa_contrato', 'parcelas']