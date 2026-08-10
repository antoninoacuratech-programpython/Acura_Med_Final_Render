from django.contrib import admin

from .hospital import Hospital
from .departamento import Departamento
from .especialidade import Especialidade


admin.site.register(Hospital)
admin.site.register(Departamento)
admin.site.register(Especialidade)