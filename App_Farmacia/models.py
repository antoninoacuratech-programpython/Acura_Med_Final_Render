# Os models desta app ficam divididos num ficheiro por model (mesmo padrão
# usado em App_Usuarios: paciente.py, endereco.py, etc.). Este ficheiro só
# agrega os imports — é dele que o Django lê para detectar os models e
# gerar as migrations.

from .medicamento import Medicamento
from .lote import Lote

__all__ = [
    "Medicamento",
    "Lote",
]