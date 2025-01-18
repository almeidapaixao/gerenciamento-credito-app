from rest_framework import serializers
from .models import Contrato, Parcela

class ParcelaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Parcela.

    Atributos:
        Meta (class): Metadados para o serializer.
            model (Parcela): Modelo que será serializado.
            fields (list): Lista de campos que serão incluídos na serialização.
                - id: Identificador único da parcela.
                - numero_parcela: Número da parcela.
                - valor_parcela: Valor da parcela.
                - data_vencimento: Data de vencimento da parcela.
    """
    class Meta:
        model = Parcela
        fields = ['id', 'numero_parcela', 'valor_parcela', 'data_vencimento']

class ContratoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Contrato, que inclui a serialização aninhada do modelo Parcela.
    Campos:
        - id: Identificador único do contrato.
        - data_emissao: Data de emissão do contrato.
        - data_nascimento_tomador: Data de nascimento do tomador do contrato.
        - valor_desembolsado: Valor desembolsado no contrato.
        - numero_documento: Número do documento do tomador.
        - endereco_tomador: Endereço do tomador do contrato.
        - telefone_tomador: Telefone do tomador do contrato.
        - taxa_contrato: Taxa aplicada ao contrato.
        - parcelas: Lista de parcelas associadas ao contrato.
    Métodos:
        - create(self, validated_data): Cria um novo contrato e suas parcelas associadas.
        - update(self, instance, validated_data): Atualiza um contrato existente e suas parcelas associadas.
    """
    parcelas = ParcelaSerializer(many=True)

    class Meta:
        model = Contrato
        fields = ['id', 'data_emissao', 'data_nascimento_tomador', 'valor_desembolsado', 
                  'numero_documento', 'endereco_tomador', 'telefone_tomador', 'taxa_contrato', 'parcelas']

    def create(self, validated_data):
        parcelas_data = validated_data.pop('parcelas')

        contrato = Contrato.objects.create(**validated_data)

        for parcela_data in parcelas_data:
            Parcela.objects.create(contrato=contrato, **parcela_data)

        return contrato

    def update(self, instance, validated_data):
        parcelas_data = validated_data.pop('parcelas', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for parcela_data in parcelas_data:
            parcela_id = parcela_data.get('id', None)
            if parcela_id:
                parcela = Parcela.objects.get(id=parcela_id, contrato=instance)
                for key, value in parcela_data.items():
                    setattr(parcela, key, value)
                parcela.save()
            else:
                Parcela.objects.create(contrato=instance, **parcela_data)

        return instance
