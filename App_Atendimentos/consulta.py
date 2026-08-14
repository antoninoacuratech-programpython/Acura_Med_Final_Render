from django.db import models

from .atendimento import Atendimento


# Ficha clínica de um atendimento — sinais vitais, avaliação e conduta do
# médico. Relação 1:1 com Atendimento: cada atendimento tem no máximo uma
# consulta (criada automaticamente na primeira vez que o médico abre a
# ficha). "rascunho" distingue entre "Salvar Rascunho" (o médico ainda está
# a preencher) e "Finalizar Atendimento" (fecha o caso).
class Consulta(models.Model):

    class Conduta(models.TextChoices):
        SOLICITAR_EXAME = "SOLICITAR_EXAME", "Solicitar Exame"
        INTERNAR = "INTERNAR", "Internar"
        ALTA = "ALTA", "Alta"
        PRESCRICAO = "PRESCRICAO", "Prescrição"

    atendimento = models.OneToOneField(
        Atendimento,
        on_delete=models.CASCADE,
        related_name="consulta",
        verbose_name="Atendimento",
    )

    # --- Sinais vitais ---
    pressao_arterial = models.CharField(
        "Pressão Arterial", max_length=15, blank=True, help_text="Ex.: 120/80"
    )
    frequencia_cardiaca = models.PositiveIntegerField(
        "Frequência Cardíaca (bpm)", blank=True, null=True
    )
    frequencia_respiratoria = models.PositiveIntegerField(
        "Frequência Respiratória (irpm)", blank=True, null=True
    )
    temperatura = models.DecimalField(
        "Temperatura (°C)", max_digits=4, decimal_places=1, blank=True, null=True
    )
    saturacao_o2 = models.PositiveIntegerField(
        "Saturação O2 (%)", blank=True, null=True
    )
    glicemia_capilar = models.PositiveIntegerField(
        "Glicemia Capilar (mg/dL)", blank=True, null=True
    )

    # --- Avaliação clínica ---
    queixa_historia_atual = models.TextField(
        "Queixa e História Atual", blank=True, max_length=2000
    )
    exame_fisico = models.TextField(
        "Exame Físico", blank=True, max_length=2000
    )
    diagnostico_clinico = models.TextField(
        "Diagnóstico Clínico", blank=True, max_length=1000
    )

    # --- Conduta ---
    conduta = models.CharField(
        "Conduta", max_length=20, choices=Conduta.choices, blank=True
    )
    observacoes_condutas = models.TextField(
        "Observações / Condutas Adicionais", blank=True, max_length=1000
    )

    rascunho = models.BooleanField("Rascunho", default=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"Consulta de {self.atendimento.paciente.nome_completo}"

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"