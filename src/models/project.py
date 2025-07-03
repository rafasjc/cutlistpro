"""
Modelo de Projeto para CutList Pro
"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Project:
    """Modelo de projeto para marcenaria"""
    
    id: int
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y %H:%M"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y %H:%M"))
    status: str = "Em desenvolvimento"
    user_id: Optional[int] = None
    components: List[Dict] = field(default_factory=list)
    cutting_diagrams: List[Dict] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if not self.settings:
            self.settings = {
                'kerf_width': 3.0,
                'optimization_algorithm': 'bottom_left_fill',
                'waste_factor': 0.15,
                'profit_margin': 0.20
            }
    
    def add_component(self, component: Dict) -> None:
        """Adicionar componente ao projeto"""
        component['id'] = len(self.components) + 1
        component['project_id'] = self.id
        self.components.append(component)
        self.update_timestamp()
    
    def remove_component(self, component_id: int) -> bool:
        """Remover componente do projeto"""
        initial_length = len(self.components)
        self.components = [c for c in self.components if c.get('id') != component_id]
        
        if len(self.components) < initial_length:
            self.update_timestamp()
            return True
        return False
    
    def update_component(self, component_id: int, updates: Dict) -> bool:
        """Atualizar componente específico"""
        for i, component in enumerate(self.components):
            if component.get('id') == component_id:
                self.components[i].update(updates)
                self.update_timestamp()
                return True
        return False
    
    def get_component_by_id(self, component_id: int) -> Optional[Dict]:
        """Buscar componente por ID"""
        return next((c for c in self.components if c.get('id') == component_id), None)
    
    def get_components_by_material(self, material_id: int) -> List[Dict]:
        """Buscar componentes por material"""
        return [c for c in self.components if c.get('material_id') == material_id]
    
    def calculate_total_area(self) -> float:
        """Calcular área total de todos os componentes (m²)"""
        total_area = 0
        for component in self.components:
            area = (component.get('length', 0) * component.get('width', 0)) / 1000000  # mm² para m²
            quantity = component.get('quantity', 1)
            total_area += area * quantity
        return total_area
    
    def calculate_total_volume(self) -> float:
        """Calcular volume total de todos os componentes (m³)"""
        total_volume = 0
        for component in self.components:
            volume = (
                component.get('length', 0) * 
                component.get('width', 0) * 
                component.get('thickness', 0)
            ) / 1000000000  # mm³ para m³
            quantity = component.get('quantity', 1)
            total_volume += volume * quantity
        return total_volume
    
    def get_materials_summary(self) -> Dict[int, Dict]:
        """Obter resumo de materiais utilizados"""
        materials_summary = {}
        
        for component in self.components:
            material_id = component.get('material_id')
            if not material_id:
                continue
            
            if material_id not in materials_summary:
                materials_summary[material_id] = {
                    'total_area': 0,
                    'total_volume': 0,
                    'component_count': 0,
                    'components': []
                }
            
            area = (component.get('length', 0) * component.get('width', 0)) / 1000000
            volume = (
                component.get('length', 0) * 
                component.get('width', 0) * 
                component.get('thickness', 0)
            ) / 1000000000
            quantity = component.get('quantity', 1)
            
            materials_summary[material_id]['total_area'] += area * quantity
            materials_summary[material_id]['total_volume'] += volume * quantity
            materials_summary[material_id]['component_count'] += quantity
            materials_summary[material_id]['components'].append(component)
        
        return materials_summary
    
    def add_cutting_diagram(self, diagram: Dict) -> None:
        """Adicionar diagrama de corte"""
        diagram['id'] = len(self.cutting_diagrams) + 1
        diagram['project_id'] = self.id
        diagram['created_at'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cutting_diagrams.append(diagram)
        self.update_timestamp()
    
    def get_latest_cutting_diagram(self) -> Optional[Dict]:
        """Obter diagrama de corte mais recente"""
        if self.cutting_diagrams:
            return self.cutting_diagrams[-1]
        return None
    
    def update_settings(self, new_settings: Dict) -> None:
        """Atualizar configurações do projeto"""
        self.settings.update(new_settings)
        self.update_timestamp()
    
    def update_timestamp(self) -> None:
        """Atualizar timestamp de modificação"""
        self.updated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def to_dict(self) -> Dict:
        """Converter projeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'user_id': self.user_id,
            'components': self.components,
            'cutting_diagrams': self.cutting_diagrams,
            'settings': self.settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        """Criar projeto a partir de dicionário"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            created_at=data.get('created_at', datetime.now().strftime("%d/%m/%Y %H:%M")),
            updated_at=data.get('updated_at', datetime.now().strftime("%d/%m/%Y %H:%M")),
            status=data.get('status', 'Em desenvolvimento'),
            user_id=data.get('user_id'),
            components=data.get('components', []),
            cutting_diagrams=data.get('cutting_diagrams', []),
            settings=data.get('settings', {})
        )
    
    def export_to_json(self) -> str:
        """Exportar projeto para JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def import_from_json(cls, json_str: str) -> 'Project':
        """Importar projeto de JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validar projeto e retornar lista de erros"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Nome do projeto é obrigatório")
        
        if len(self.name) > 100:
            errors.append("Nome do projeto deve ter no máximo 100 caracteres")
        
        if len(self.description) > 500:
            errors.append("Descrição deve ter no máximo 500 caracteres")
        
        # Validar componentes
        for i, component in enumerate(self.components):
            component_errors = self._validate_component(component, i)
            errors.extend(component_errors)
        
        return errors
    
    def _validate_component(self, component: Dict, index: int) -> List[str]:
        """Validar componente individual"""
        errors = []
        prefix = f"Componente {index + 1}: "
        
        if not component.get('name'):
            errors.append(f"{prefix}Nome é obrigatório")
        
        for dimension in ['length', 'width', 'thickness']:
            value = component.get(dimension, 0)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"{prefix}{dimension.capitalize()} deve ser um número positivo")
        
        quantity = component.get('quantity', 1)
        if not isinstance(quantity, int) or quantity <= 0:
            errors.append(f"{prefix}Quantidade deve ser um número inteiro positivo")
        
        if not component.get('material_id'):
            errors.append(f"{prefix}Material é obrigatório")
        
        return errors
    
    def __str__(self) -> str:
        """Representação string do projeto"""
        return f"Project(id={self.id}, name='{self.name}', components={len(self.components)})"
    
    def __repr__(self) -> str:
        """Representação detalhada do projeto"""
        return (f"Project(id={self.id}, name='{self.name}', "
                f"description='{self.description[:50]}...', "
                f"components={len(self.components)}, "
                f"status='{self.status}')")


# Funções utilitárias para gerenciamento de projetos

def create_sample_project() -> Project:
    """Criar projeto de exemplo"""
    project = Project(
        id=1,
        name="Estante de Livros",
        description="Estante simples com 3 prateleiras"
    )
    
    # Adicionar componentes de exemplo
    components = [
        {
            'name': 'Lateral Esquerda',
            'length': 600.0,
            'width': 300.0,
            'thickness': 15.0,
            'quantity': 1,
            'material_id': 1
        },
        {
            'name': 'Lateral Direita',
            'length': 600.0,
            'width': 300.0,
            'thickness': 15.0,
            'quantity': 1,
            'material_id': 1
        },
        {
            'name': 'Fundo',
            'length': 570.0,
            'width': 270.0,
            'thickness': 15.0,
            'quantity': 1,
            'material_id': 1
        },
        {
            'name': 'Prateleira',
            'length': 570.0,
            'width': 270.0,
            'thickness': 15.0,
            'quantity': 3,
            'material_id': 1
        }
    ]
    
    for component in components:
        project.add_component(component)
    
    return project


def validate_project_data(data: Dict) -> List[str]:
    """Validar dados de projeto antes da criação"""
    errors = []
    
    required_fields = ['name']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Campo '{field}' é obrigatório")
    
    if 'name' in data and len(data['name']) > 100:
        errors.append("Nome deve ter no máximo 100 caracteres")
    
    if 'description' in data and len(data['description']) > 500:
        errors.append("Descrição deve ter no máximo 500 caracteres")
    
    return errors

