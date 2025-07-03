"""
Modelo de Componente para CutList Pro
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json


@dataclass
class Component:
    """Modelo de componente/peça para marcenaria"""
    
    id: int
    name: str
    length: float  # mm
    width: float   # mm
    thickness: float  # mm
    quantity: int = 1
    material_id: Optional[int] = None
    project_id: Optional[int] = None
    description: str = ""
    edge_banding: Dict[str, bool] = field(default_factory=lambda: {
        'top': False,
        'bottom': False,
        'left': False,
        'right': False
    })
    grain_direction: str = "length"  # "length" ou "width"
    priority: int = 1  # 1-5, sendo 5 a maior prioridade
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        self.validate_dimensions()
        self.validate_quantity()
    
    def validate_dimensions(self) -> None:
        """Validar dimensões do componente"""
        if self.length <= 0:
            raise ValueError("Comprimento deve ser maior que zero")
        if self.width <= 0:
            raise ValueError("Largura deve ser maior que zero")
        if self.thickness <= 0:
            raise ValueError("Espessura deve ser maior que zero")
    
    def validate_quantity(self) -> None:
        """Validar quantidade"""
        if not isinstance(self.quantity, int) or self.quantity <= 0:
            raise ValueError("Quantidade deve ser um número inteiro positivo")
    
    def get_area(self) -> float:
        """Calcular área do componente em m²"""
        return (self.length * self.width) / 1000000
    
    def get_volume(self) -> float:
        """Calcular volume do componente em m³"""
        return (self.length * self.width * self.thickness) / 1000000000
    
    def get_total_area(self) -> float:
        """Calcular área total considerando quantidade"""
        return self.get_area() * self.quantity
    
    def get_total_volume(self) -> float:
        """Calcular volume total considerando quantidade"""
        return self.get_volume() * self.quantity
    
    def get_perimeter(self) -> float:
        """Calcular perímetro em mm"""
        return 2 * (self.length + self.width)
    
    def get_edge_banding_length(self) -> Dict[str, float]:
        """Calcular comprimento de fita de borda necessária"""
        edge_lengths = {
            'top': self.length if self.edge_banding['top'] else 0,
            'bottom': self.length if self.edge_banding['bottom'] else 0,
            'left': self.width if self.edge_banding['left'] else 0,
            'right': self.width if self.edge_banding['right'] else 0
        }
        return edge_lengths
    
    def get_total_edge_banding_length(self) -> float:
        """Calcular comprimento total de fita de borda"""
        edge_lengths = self.get_edge_banding_length()
        total_length = sum(edge_lengths.values())
        return total_length * self.quantity
    
    def set_edge_banding(self, edges: Dict[str, bool]) -> None:
        """Configurar fita de borda"""
        valid_edges = {'top', 'bottom', 'left', 'right'}
        for edge, value in edges.items():
            if edge in valid_edges:
                self.edge_banding[edge] = bool(value)
    
    def set_all_edges(self, value: bool) -> None:
        """Configurar todas as bordas"""
        for edge in self.edge_banding:
            self.edge_banding[edge] = value
    
    def get_dimensions_tuple(self) -> Tuple[float, float, float]:
        """Obter dimensões como tupla (length, width, thickness)"""
        return (self.length, self.width, self.thickness)
    
    def get_dimensions_dict(self) -> Dict[str, float]:
        """Obter dimensões como dicionário"""
        return {
            'length': self.length,
            'width': self.width,
            'thickness': self.thickness
        }
    
    def fits_in_sheet(self, sheet_width: float, sheet_height: float) -> bool:
        """Verificar se o componente cabe na chapa"""
        # Verificar ambas as orientações
        orientation1 = (self.length <= sheet_width and self.width <= sheet_height)
        orientation2 = (self.width <= sheet_width and self.length <= sheet_height)
        return orientation1 or orientation2
    
    def get_best_orientation(self, sheet_width: float, sheet_height: float) -> Optional[str]:
        """Obter melhor orientação para a chapa"""
        orientation1_fits = (self.length <= sheet_width and self.width <= sheet_height)
        orientation2_fits = (self.width <= sheet_width and self.length <= sheet_height)
        
        if not (orientation1_fits or orientation2_fits):
            return None
        
        # Priorizar orientação baseada na direção da fibra
        if self.grain_direction == "length":
            if orientation1_fits:
                return "normal"  # length = width da chapa
            elif orientation2_fits:
                return "rotated"  # length = height da chapa
        else:  # grain_direction == "width"
            if orientation2_fits:
                return "rotated"
            elif orientation1_fits:
                return "normal"
        
        # Se ambas cabem, escolher a que desperdiça menos
        if orientation1_fits and orientation2_fits:
            waste1 = (sheet_width * sheet_height) - (self.length * self.width)
            waste2 = (sheet_width * sheet_height) - (self.width * self.length)
            return "normal" if waste1 <= waste2 else "rotated"
        
        return "normal" if orientation1_fits else "rotated"
    
    def calculate_weight(self, material_density: float) -> float:
        """Calcular peso do componente em kg"""
        volume_m3 = self.get_volume()
        return volume_m3 * material_density * self.quantity
    
    def add_tag(self, tag: str) -> None:
        """Adicionar tag ao componente"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> bool:
        """Remover tag do componente"""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """Verificar se componente tem tag específica"""
        return tag in self.tags
    
    def set_custom_property(self, key: str, value) -> None:
        """Definir propriedade customizada"""
        self.custom_properties[key] = value
    
    def get_custom_property(self, key: str, default=None):
        """Obter propriedade customizada"""
        return self.custom_properties.get(key, default)
    
    def to_dict(self) -> Dict:
        """Converter componente para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'length': self.length,
            'width': self.width,
            'thickness': self.thickness,
            'quantity': self.quantity,
            'material_id': self.material_id,
            'project_id': self.project_id,
            'description': self.description,
            'edge_banding': self.edge_banding,
            'grain_direction': self.grain_direction,
            'priority': self.priority,
            'tags': self.tags,
            'custom_properties': self.custom_properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Component':
        """Criar componente a partir de dicionário"""
        return cls(
            id=data['id'],
            name=data['name'],
            length=data['length'],
            width=data['width'],
            thickness=data['thickness'],
            quantity=data.get('quantity', 1),
            material_id=data.get('material_id'),
            project_id=data.get('project_id'),
            description=data.get('description', ''),
            edge_banding=data.get('edge_banding', {
                'top': False, 'bottom': False, 'left': False, 'right': False
            }),
            grain_direction=data.get('grain_direction', 'length'),
            priority=data.get('priority', 1),
            tags=data.get('tags', []),
            custom_properties=data.get('custom_properties', {})
        )
    
    def clone(self, new_id: int, new_name: Optional[str] = None) -> 'Component':
        """Criar cópia do componente"""
        data = self.to_dict()
        data['id'] = new_id
        if new_name:
            data['name'] = new_name
        return Component.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validar componente e retornar lista de erros"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Nome do componente é obrigatório")
        
        if len(self.name) > 100:
            errors.append("Nome deve ter no máximo 100 caracteres")
        
        try:
            self.validate_dimensions()
        except ValueError as e:
            errors.append(str(e))
        
        try:
            self.validate_quantity()
        except ValueError as e:
            errors.append(str(e))
        
        if self.priority < 1 or self.priority > 5:
            errors.append("Prioridade deve estar entre 1 e 5")
        
        if self.grain_direction not in ['length', 'width']:
            errors.append("Direção da fibra deve ser 'length' ou 'width'")
        
        return errors
    
    def __str__(self) -> str:
        """Representação string do componente"""
        return f"Component('{self.name}', {self.length}x{self.width}x{self.thickness}mm, qty={self.quantity})"
    
    def __repr__(self) -> str:
        """Representação detalhada do componente"""
        return (f"Component(id={self.id}, name='{self.name}', "
                f"dimensions=({self.length}, {self.width}, {self.thickness}), "
                f"quantity={self.quantity}, material_id={self.material_id})")


# Funções utilitárias para componentes

def create_component_from_dimensions(
    name: str,
    length: float,
    width: float,
    thickness: float,
    quantity: int = 1,
    material_id: Optional[int] = None
) -> Component:
    """Criar componente a partir de dimensões"""
    return Component(
        id=0,  # Será definido ao adicionar ao projeto
        name=name,
        length=length,
        width=width,
        thickness=thickness,
        quantity=quantity,
        material_id=material_id
    )


def sort_components_by_area(components: List[Component], descending: bool = True) -> List[Component]:
    """Ordenar componentes por área"""
    return sorted(components, key=lambda c: c.get_area(), reverse=descending)


def sort_components_by_priority(components: List[Component], descending: bool = True) -> List[Component]:
    """Ordenar componentes por prioridade"""
    return sorted(components, key=lambda c: c.priority, reverse=descending)


def filter_components_by_material(components: List[Component], material_id: int) -> List[Component]:
    """Filtrar componentes por material"""
    return [c for c in components if c.material_id == material_id]


def filter_components_by_thickness(components: List[Component], thickness: float) -> List[Component]:
    """Filtrar componentes por espessura"""
    return [c for c in components if c.thickness == thickness]


def group_components_by_material(components: List[Component]) -> Dict[int, List[Component]]:
    """Agrupar componentes por material"""
    groups = {}
    for component in components:
        material_id = component.material_id or 0
        if material_id not in groups:
            groups[material_id] = []
        groups[material_id].append(component)
    return groups


def calculate_total_area(components: List[Component]) -> float:
    """Calcular área total de uma lista de componentes"""
    return sum(c.get_total_area() for c in components)


def calculate_total_volume(components: List[Component]) -> float:
    """Calcular volume total de uma lista de componentes"""
    return sum(c.get_total_volume() for c in components)


def validate_components_list(components: List[Component]) -> List[str]:
    """Validar lista de componentes"""
    errors = []
    
    if not components:
        errors.append("Lista de componentes não pode estar vazia")
        return errors
    
    # Verificar IDs únicos
    ids = [c.id for c in components]
    if len(ids) != len(set(ids)):
        errors.append("IDs de componentes devem ser únicos")
    
    # Validar cada componente
    for i, component in enumerate(components):
        component_errors = component.validate()
        for error in component_errors:
            errors.append(f"Componente {i+1}: {error}")
    
    return errors

