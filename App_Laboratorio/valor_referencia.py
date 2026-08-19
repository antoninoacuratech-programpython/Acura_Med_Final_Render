from django.db import models

from .parametro import Parametro


# Cada linha é uma faixa de referência para um Parametro, específica de
# um grupo (sexo + intervalo de idade). Um mesmo parâmetro pode ter
# várias linhas — ex.: Hemoglobina tem uma faixa para Masculino 18-120
# e outra para Feminino 18-120. O sistema escolhe automaticamente a
# linha certa comparando sexo/idade do paciente.
class ValorReferencia(models.Model):

    class Sexo(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMININO = "F", "Feminino"
        AMBOS = "AMBOS", "Ambos"

    class Sinal(models.TextChoices):
        MAIOR = ">", ">"
        MAIOR_IGUAL = ">=", ">="
        MENOR = "<", "<"
        MENOR_IGUAL = "<=", "<="
        NENHUM = "-", "-"

    parametro = models.ForeignKey(
        Parametro,
        on_delete=models.CASCADE,
        related_name="valores_referencia",
        verbose_name="Parâmetro",
    )

    grupo = models.CharField(
        "Grupo",
        max_length=50,
        default="Adulto",
        help_text="Ex.: Adulto, Criança, Recém-nascido",
    )

    sexo = models.CharField(
        "Sexo",
        max_length=5,
        choices=Sexo.choices,
        default=Sexo.AMBOS,
    )

    idade_minima = models.DecimalField(
        "Idade Mínima (anos)",
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
    )

    idade_maxima = models.DecimalField(
        "Idade Máxima (anos)",
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
    )

    sinal_minimo = models.CharField(
        "Sinal Mín.",
        max_length=2,
        choices=Sinal.choices,
        default=Sinal.NENHUM,
    )

    valor_minimo = models.DecimalField(
        "Valor Mínimo",
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
    )

    sinal_maximo = models.CharField(
        "Sinal Máx.",
        max_length=2,
        choices=Sinal.choices,
        default=Sinal.NENHUM,
    )

    valor_maximo = models.DecimalField(
        "Valor Máximo",
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
    )

    critico_minimo = models.DecimalField(
        "Crítico Mínimo",
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Abaixo deste valor, o resultado é sinalizado como crítico",
    )

    critico_maximo = models.DecimalField(
        "Crítico Máximo",
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Acima deste valor, o resultado é sinalizado como crítico",
    )

    valor_texto = models.CharField(
        "Referência Textual",
        max_length=150,
        blank=True,
        help_text="Ex.: 'Negativo' — usado quando o parâmetro não é numérico",
    )

    observacoes = models.CharField(
        "Observações",
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.parametro.nome} — {self.grupo}/{self.get_sexo_display()} ({self.idade_minima or 0}-{self.idade_maxima or '∞'} anos)"

    class Meta:
        verbose_name = "Valor de Referência"
        verbose_name_plural = "Valores de Referência"
        ordering = ["parametro__nome", "grupo", "sexo", "idade_minima"]