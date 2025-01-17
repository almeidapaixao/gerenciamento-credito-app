from django.db import models


class Contrato(models.Model):
    id = models.AutoField(primary_key=True)
    data_emissao = models.DateField()
    data_nascimento_tomador = models.DateField()
    valor_desembolsado = models.DecimalField(max_digits=10, decimal_places=2)
    numero_documento = models.CharField(max_length=14)  # CPF do tomador
    endereco_tomador = models.JSONField()  # País, Estado, Cidade
    telefone_tomador = models.CharField(max_length=15)  # Número de telefone
    taxa_contrato = models.DecimalField(max_digits=5, decimal_places=2)  # Taxa do contrato

    def __str__(self):
        return f"Contrato {self.id}"

class Parcela(models.Model):
    contrato = models.ForeignKey(Contrato, related_name="parcelas", on_delete=models.CASCADE)
    numero_parcela = models.IntegerField()
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()

    def __str__(self):
        return f"Parcela {self.numero_parcela} do Contrato {self.contrato.id}"