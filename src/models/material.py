"""
Modelo de Material para CutList Pro
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json


@dataclass
class Material:
    """Modelo de material para marcenaria"""
    
    id: int
    name: str
    thickness: float  # mm
    price_per_unit: float  # preço por unidade (m², m³, m, peça)
    price_unit: str = "m²"  # unidade de preço
    density: float = 750.0  # kg/m³
    standard_sizes: List[Tuple[int, int]] = field(default_factory=list)  # (width, height) em mm
    description: str = ""
    category: str = "Madeira"
    supplier: str = ""
    color: str = "#8B4513"  # cor para visualização
    grain_direction: str = "length"  # direção preferencial da fibra
    properties: Dict = field(default_factory=dict)
    is_active: bool = True
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if not self.standard_sizes:
            # Tamanhos padrão comuns para chapas
            self.standard_sizes = [(2750, 1830), (2440, 1220)]
        
        if not self.properties:
            self.properties = {
                'moisture_content': 8.0,  # % umidade
                'hardness': 'medium',     # soft, medium, hard
                'finish': 'raw',          # raw, laminated, veneer
                'fire_resistance': 'standard',
                'water_resistance': 'low'
            }
    
    def get_largest_sheet_size(self) -> Tuple[int, int]:
        """Obter maior tamanho de chapa disponível"""
        if not self.standard_sizes:
            return (2750, 1830)  # Padrão
        
        return max(self.standard_sizes, key=lambda size: size[0] * size[1])
    
    def get_sheet_area(self, size_index: int = 0) -> float:
        """Obter área da chapa em m²"""
        if not self.standard_sizes or size_index >= len(self.standard_sizes):
            return 0.0
        
        width, height = self.standard_sizes[size_index]
        return (width * height) / 1000000
    
    def calculate_price_per_m2(self) -> float:
        """Calcular preço por m² independente da unidade"""
        if self.price_unit == "m²":
            return self.price_per_unit
        elif self.price_unit == "m³":
            # Converter de m³ para m² usando espessura
            thickness_m = self.thickness / 1000
            return self.price_per_unit * thickness_m
        elif self.price_unit == "m":
            # Para materiais lineares, assumir largura padrão
            default_width = 0.1  # 10cm
            return self.price_per_unit / default_width
        elif self.price_unit == "piece":
            # Para peças, usar área da maior chapa
            largest_area = self.get_sheet_area(0)
            return self.price_per_unit / largest_area if largest_area > 0 else 0
        else:
            return self.price_per_unit
    
    def calculate_cost_for_area(self, area_m2: float) -> float:
        """Calcular custo para uma área específica"""
        price_per_m2 = self.calculate_price_per_m2()
        return area_m2 * price_per_m2
    
    def calculate_cost_for_volume(self, volume_m3: float) -> float:
        """Calcular custo para um volume específico"""
        if self.price_unit == "m³":
            return volume_m3 * self.price_per_unit
        else:
            # Converter volume para área
            thickness_m = self.thickness / 1000
            area_m2 = volume_m3 / thickness_m if thickness_m > 0 else 0
            return self.calculate_cost_for_area(area_m2)
    
    def calculate_weight(self, area_m2: float) -> float:
        """Calcular peso para uma área específica"""
        thickness_m = self.thickness / 1000
        volume_m3 = area_m2 * thickness_m
        return volume_m3 * self.density
    
    def get_sheets_needed(self, total_area_m2: float, waste_factor: float = 0.15) -> int:
        """Calcular número de chapas necessárias"""
        if not self.standard_sizes:
            return 0
        
        # Usar a maior chapa disponível
        sheet_area = self.get_sheet_area(0)
        if sheet_area <= 0:
            return 0
        
        # Aplicar fator de desperdício
        effective_area = sheet_area * (1 - waste_factor)
        
        if effective_area <= 0:
            return 0
        
        return max(1, int(total_area_m2 / effective_area) + (1 if total_area_m2 % effective_area > 0 else 0))
    
    def calculate_total_cost(self, total_area_m2: float, waste_factor: float = 0.15) -> Dict[str, float]:
        """Calcular custo total incluindo desperdício"""
        sheets_needed = self.get_sheets_needed(total_area_m2, waste_factor)
        sheet_area = self.get_sheet_area(0)
        
        total_sheet_area = sheets_needed * sheet_area
        material_cost = self.calculate_cost_for_area(total_sheet_area)
        waste_area = total_sheet_area - total_area_m2
        waste_cost = self.calculate_cost_for_area(waste_area)
        
        return {
            'material_cost': material_cost,
            'waste_cost': waste_cost,
            'total_cost': material_cost,
            'sheets_needed': sheets_needed,
            'total_area': total_sheet_area,
            'waste_area': waste_area,
            'utilization': (total_area_m2 / total_sheet_area * 100) if total_sheet_area > 0 else 0
        }
    
    def add_standard_size(self, width: int, height: int) -> None:
        """Adicionar tamanho padrão"""
        size = (width, height)
        if size not in self.standard_sizes:
            self.standard_sizes.append(size)
    
    def remove_standard_size(self, width: int, height: int) -> bool:
        """Remover tamanho padrão"""
        size = (width, height)
        if size in self.standard_sizes:
            self.standard_sizes.remove(size)
            return True
        return False
    
    def set_property(self, key: str, value) -> None:
        """Definir propriedade do material"""
        self.properties[key] = value
    
    def get_property(self, key: str, default=None):
        """Obter propriedade do material"""
        return self.properties.get(key, default)
    
    def is_compatible_thickness(self, thickness: float, tolerance: float = 0.5) -> bool:
        """Verificar se espessura é compatível"""
        return abs(self.thickness - thickness) <= tolerance
    
    def get_display_name(self) -> str:
        """Obter nome para exibição"""
        return f"{self.name} {self.thickness}mm"
    
    def get_price_display(self) -> str:
        """Obter preço formatado para exibição"""
        return f"R$ {self.price_per_unit:.2f}/{self.price_unit}"
    
    def to_dict(self) -> Dict:
        """Converter material para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'thickness': self.thickness,
            'price_per_unit': self.price_per_unit,
            'price_unit': self.price_unit,
            'density': self.density,
            'standard_sizes': self.standard_sizes,
            'description': self.description,
            'category': self.category,
            'supplier': self.supplier,
            'color': self.color,
            'grain_direction': self.grain_direction,
            'properties': self.properties,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Material':
        """Criar material a partir de dicionário"""
        return cls(
            id=data['id'],
            name=data['name'],
            thickness=data['thickness'],
            price_per_unit=data['price_per_unit'],
            price_unit=data.get('price_unit', 'm²'),
            density=data.get('density', 750.0),
            standard_sizes=data.get('standard_sizes', []),
            description=data.get('description', ''),
            category=data.get('category', 'Madeira'),
            supplier=data.get('supplier', ''),
            color=data.get('color', '#8B4513'),
            grain_direction=data.get('grain_direction', 'length'),
            properties=data.get('properties', {}),
            is_active=data.get('is_active', True)
        )
    
    def clone(self, new_id: int, new_name: Optional[str] = None) -> 'Material':
        """Criar cópia do material"""
        data = self.to_dict()
        data['id'] = new_id
        if new_name:
            data['name'] = new_name
        return Material.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validar material e retornar lista de erros"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Nome do material é obrigatório")
        
        if len(self.name) > 100:
            errors.append("Nome deve ter no máximo 100 caracteres")
        
        if self.thickness <= 0:
            errors.append("Espessura deve ser maior que zero")
        
        if self.price_per_unit <= 0:
            errors.append("Preço deve ser maior que zero")
        
        if self.price_unit not in ['m²', 'm³', 'm', 'piece']:
            errors.append("Unidade de preço deve ser m², m³, m ou piece")
        
        if self.density <= 0:
            errors.append("Densidade deve ser maior que zero")
        
        if self.grain_direction not in ['length', 'width']:
            errors.append("Direção da fibra deve ser 'length' ou 'width'")
        
        # Validar tamanhos padrão
        for i, size in enumerate(self.standard_sizes):
            if not isinstance(size, (tuple, list)) or len(size) != 2:
                errors.append(f"Tamanho padrão {i+1} deve ser uma tupla (largura, altura)")
                continue
            
            width, height = size
            if not isinstance(width, (int, float)) or width <= 0:
                errors.append(f"Largura do tamanho padrão {i+1} deve ser maior que zero")
            
            if not isinstance(height, (int, float)) or height <= 0:
                errors.append(f"Altura do tamanho padrão {i+1} deve ser maior que zero")
        
        return errors
    
    def __str__(self) -> str:
        """Representação string do material"""
        return f"Material('{self.name}', {self.thickness}mm, {self.get_price_display()})"
    
    def __repr__(self) -> str:
        """Representação detalhada do material"""
        return (f"Material(id={self.id}, name='{self.name}', "
                f"thickness={self.thickness}, price={self.price_per_unit}, "
                f"unit='{self.price_unit}', category='{self.category}')")


# Funções utilitárias para materiais

def create_default_materials() -> List[Material]:
    """Criar lista de materiais padrão"""
    materials = [
        Material(
            id=1,
            name="MDF",
            thickness=15.0,
            price_per_unit=80.00,
            price_unit="m²",
            density=750.0,
            standard_sizes=[(2750, 1830), (2440, 1220)],
            description="MDF de média densidade, ideal para móveis",
            category="Madeira Reconstituída",
            color="#D2B48C"
        ),
        Material(
            id=2,
            name="Compensado",
            thickness=18.0,
            price_per_unit=120.00,
            price_unit="m²",
            density=600.0,
            standard_sizes=[(2200, 1600)],
            description="Compensado multilaminado de alta qualidade",
            category="Madeira Laminada",
            color="#DEB887"
        ),
        Material(
            id=3,
            name="Pinus",
            thickness=25.0,
            price_per_unit=15.00,
            price_unit="m",
            density=500.0,
            standard_sizes=[(3000, 89), (3000, 140)],
            description="Madeira de pinus para estruturas",
            category="Madeira Maciça",
            color="#F4A460"
        ),
        Material(
            id=4,
            name="MDP",
            thickness=15.0,
            price_per_unit=65.00,
            price_unit="m²",
            density=680.0,
            standard_sizes=[(2750, 1830)],
            description="MDP com revestimento melamínico",
            category="Madeira Reconstituída",
            color="#CD853F"
        ),
        Material(
            id=5,
            name="OSB",
            thickness=12.0,
            price_per_unit=45.00,
            price_unit="m²",
            density=650.0,
            standard_sizes=[(2440, 1220)],
            description="OSB para estruturas e fechamentos",
            category="Madeira Reconstituída",
            color="#DAA520"
        )
    ]
    
    return materials


def filter_materials_by_category(materials: List[Material], category: str) -> List[Material]:
    """Filtrar materiais por categoria"""
    return [m for m in materials if m.category == category and m.is_active]


def filter_materials_by_thickness(materials: List[Material], thickness: float, tolerance: float = 0.5) -> List[Material]:
    """Filtrar materiais por espessura"""
    return [m for m in materials if m.is_compatible_thickness(thickness, tolerance) and m.is_active]


def sort_materials_by_price(materials: List[Material], descending: bool = False) -> List[Material]:
    """Ordenar materiais por preço por m²"""
    return sorted(materials, key=lambda m: m.calculate_price_per_m2(), reverse=descending)


def get_material_by_id(materials: List[Material], material_id: int) -> Optional[Material]:
    """Buscar material por ID"""
    return next((m for m in materials if m.id == material_id), None)


def calculate_project_material_costs(materials: List[Material], material_usage: Dict[int, float]) -> Dict:
    """Calcular custos de materiais para um projeto"""
    total_cost = 0
    material_costs = {}
    
    for material_id, area_needed in material_usage.items():
        material = get_material_by_id(materials, material_id)
        if material:
            cost_info = material.calculate_total_cost(area_needed)
            material_costs[material_id] = {
                'material': material,
                'area_needed': area_needed,
                'cost_info': cost_info
            }
            total_cost += cost_info['total_cost']
    
    return {
        'total_cost': total_cost,
        'material_costs': material_costs
    }


def validate_materials_list(materials: List[Material]) -> List[str]:
    """Validar lista de materiais"""
    errors = []
    
    if not materials:
        errors.append("Lista de materiais não pode estar vazia")
        return errors
    
    # Verificar IDs únicos
    ids = [m.id for m in materials]
    if len(ids) != len(set(ids)):
        errors.append("IDs de materiais devem ser únicos")
    
    # Verificar nomes únicos
    names = [m.name.lower() for m in materials]
    if len(names) != len(set(names)):
        errors.append("Nomes de materiais devem ser únicos")
    
    # Validar cada material
    for i, material in enumerate(materials):
        material_errors = material.validate()
        for error in material_errors:
            errors.append(f"Material {i+1}: {error}")
    
    return errors

