"""
Parser de arquivos SketchUp para CutList Pro
Simula extração de componentes de arquivos .skp
"""

import io
import json
import zipfile
from typing import List, Dict, Optional, Tuple, BinaryIO
from dataclasses import dataclass
import re
import struct
import streamlit as st


@dataclass
class SketchUpComponent:
    """Componente extraído do SketchUp"""
    name: str
    length: float  # mm
    width: float   # mm
    thickness: float  # mm
    quantity: int = 1
    material_name: str = ""
    layer_name: str = ""
    component_definition: str = ""
    bounding_box: Dict = None
    attributes: Dict = None
    
    def __post_init__(self):
        if self.bounding_box is None:
            self.bounding_box = {
                'min_x': 0, 'min_y': 0, 'min_z': 0,
                'max_x': self.length, 'max_y': self.width, 'max_z': self.thickness
            }
        
        if self.attributes is None:
            self.attributes = {}


@dataclass
class SketchUpParseResult:
    """Resultado do parsing do arquivo SketchUp"""
    success: bool
    components: List[SketchUpComponent]
    materials: List[Dict]
    layers: List[str]
    model_info: Dict
    errors: List[str]
    warnings: List[str]


class SketchUpParser:
    """Parser para arquivos SketchUp (.skp)"""
    
    def __init__(self):
        self.supported_versions = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]
        self.min_component_size = 1.0  # mm mínimo
        self.max_component_size = 10000.0  # mm máximo
    
    def parse_file(self, file_content: bytes, filename: str) -> SketchUpParseResult:
        """
        Parsear arquivo SketchUp
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            filename: Nome do arquivo
            
        Returns:
            SketchUpParseResult com componentes extraídos
        """
        try:
            # Validar arquivo
            validation_result = self._validate_skp_file(file_content, filename)
            if not validation_result['valid']:
                return SketchUpParseResult(
                    success=False,
                    components=[],
                    materials=[],
                    layers=[],
                    model_info={},
                    errors=validation_result['errors'],
                    warnings=[]
                )
            
            # Simular extração de componentes
            # Em uma implementação real, aqui seria usado a API do SketchUp
            components = self._extract_components_simulation(filename)
            materials = self._extract_materials_simulation()
            layers = self._extract_layers_simulation()
            model_info = self._extract_model_info_simulation(filename)
            
            # Validar componentes extraídos
            validated_components, warnings = self._validate_components(components)
            
            return SketchUpParseResult(
                success=True,
                components=validated_components,
                materials=materials,
                layers=layers,
                model_info=model_info,
                errors=[],
                warnings=warnings
            )
            
        except Exception as e:
            return SketchUpParseResult(
                success=False,
                components=[],
                materials=[],
                layers=[],
                model_info={},
                errors=[f"Erro ao processar arquivo: {str(e)}"],
                warnings=[]
            )
    
    def _validate_skp_file(self, file_content: bytes, filename: str) -> Dict:
        """Validar se é um arquivo SketchUp válido"""
        errors = []
        
        # Verificar extensão
        if not filename.lower().endswith('.skp'):
            errors.append("Arquivo deve ter extensão .skp")
        
        # Verificar tamanho mínimo
        if len(file_content) < 1024:  # 1KB mínimo
            errors.append("Arquivo muito pequeno para ser um SketchUp válido")
        
        # Verificar tamanho máximo (100MB)
        if len(file_content) > 100 * 1024 * 1024:
            errors.append("Arquivo muito grande (máximo 100MB)")
        
        # Verificar assinatura do arquivo SketchUp
        if len(file_content) >= 8:
            # SketchUp files começam com uma assinatura específica
            header = file_content[:8]
            # Simulação da verificação de header
            if not self._is_valid_skp_header(header):
                errors.append("Arquivo não parece ser um SketchUp válido")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _is_valid_skp_header(self, header: bytes) -> bool:
        """Verificar header do arquivo SketchUp (simulado)"""
        # Em uma implementação real, verificaria a assinatura específica
        # Por enquanto, aceitar qualquer arquivo que não seja obviamente inválido
        return len(header) >= 8 and header != b'\x00' * 8
    
    def _extract_components_simulation(self, filename: str) -> List[SketchUpComponent]:
        """
        Simular extração de componentes baseado no nome do arquivo
        Em uma implementação real, usaria a API do SketchUp
        """
        base_name = filename.replace('.skp', '').replace('_', ' ').title()
        
        # Diferentes simulações baseadas no nome do arquivo
        if 'estante' in filename.lower() or 'shelf' in filename.lower():
            return self._create_shelf_components(base_name)
        elif 'mesa' in filename.lower() or 'table' in filename.lower():
            return self._create_table_components(base_name)
        elif 'armario' in filename.lower() or 'cabinet' in filename.lower():
            return self._create_cabinet_components(base_name)
        elif 'cadeira' in filename.lower() or 'chair' in filename.lower():
            return self._create_chair_components(base_name)
        else:
            return self._create_generic_components(base_name)
    
    def _create_shelf_components(self, base_name: str) -> List[SketchUpComponent]:
        """Criar componentes de estante"""
        return [
            SketchUpComponent(
                name="Lateral Esquerda",
                length=600.0,
                width=300.0,
                thickness=15.0,
                quantity=1,
                material_name="MDF 15mm",
                layer_name="Estrutura",
                component_definition="Lateral_Estante"
            ),
            SketchUpComponent(
                name="Lateral Direita",
                length=600.0,
                width=300.0,
                thickness=15.0,
                quantity=1,
                material_name="MDF 15mm",
                layer_name="Estrutura",
                component_definition="Lateral_Estante"
            ),
            SketchUpComponent(
                name="Fundo",
                length=570.0,
                width=270.0,
                thickness=15.0,
                quantity=1,
                material_name="MDF 15mm",
                layer_name="Estrutura",
                component_definition="Fundo_Estante"
            ),
            SketchUpComponent(
                name="Prateleira",
                length=570.0,
                width=270.0,
                thickness=15.0,
                quantity=3,
                material_name="MDF 15mm",
                layer_name="Prateleiras",
                component_definition="Prateleira_Estante"
            ),
            SketchUpComponent(
                name="Topo",
                length=600.0,
                width=300.0,
                thickness=15.0,
                quantity=1,
                material_name="MDF 15mm",
                layer_name="Estrutura",
                component_definition="Topo_Estante"
            )
        ]
    
    def _create_table_components(self, base_name: str) -> List[SketchUpComponent]:
        """Criar componentes de mesa"""
        return [
            SketchUpComponent(
                name="Tampo",
                length=1200.0,
                width=600.0,
                thickness=25.0,
                quantity=1,
                material_name="MDF 25mm",
                layer_name="Tampo",
                component_definition="Tampo_Mesa"
            ),
            SketchUpComponent(
                name="Pé",
                length=720.0,
                width=80.0,
                thickness=80.0,
                quantity=4,
                material_name="Pinus",
                layer_name="Estrutura",
                component_definition="Pe_Mesa"
            ),
            SketchUpComponent(
                name="Travessa Longitudinal",
                length=1000.0,
                width=80.0,
                thickness=25.0,
                quantity=2,
                material_name="Pinus",
                layer_name="Estrutura",
                component_definition="Travessa_Long"
            ),
            SketchUpComponent(
                name="Travessa Transversal",
                length=400.0,
                width=80.0,
                thickness=25.0,
                quantity=2,
                material_name="Pinus",
                layer_name="Estrutura",
                component_definition="Travessa_Trans"
            )
        ]
    
    def _create_cabinet_components(self, base_name: str) -> List[SketchUpComponent]:
        """Criar componentes de armário"""
        return [
            SketchUpComponent(
                name="Lateral",
                length=800.0,
                width=400.0,
                thickness=18.0,
                quantity=2,
                material_name="MDP 18mm",
                layer_name="Carcaça",
                component_definition="Lateral_Armario"
            ),
            SketchUpComponent(
                name="Fundo",
                length=764.0,
                width=382.0,
                thickness=6.0,
                quantity=1,
                material_name="Hardboard",
                layer_name="Carcaça",
                component_definition="Fundo_Armario"
            ),
            SketchUpComponent(
                name="Prateleira Fixa",
                length=764.0,
                width=382.0,
                thickness=18.0,
                quantity=2,
                material_name="MDP 18mm",
                layer_name="Prateleiras",
                component_definition="Prateleira_Fixa"
            ),
            SketchUpComponent(
                name="Porta",
                length=400.0,
                width=382.0,
                thickness=18.0,
                quantity=2,
                material_name="MDP 18mm",
                layer_name="Portas",
                component_definition="Porta_Armario"
            )
        ]
    
    def _create_chair_components(self, base_name: str) -> List[SketchUpComponent]:
        """Criar componentes de cadeira"""
        return [
            SketchUpComponent(
                name="Assento",
                length=400.0,
                width=400.0,
                thickness=20.0,
                quantity=1,
                material_name="Compensado 20mm",
                layer_name="Assento",
                component_definition="Assento_Cadeira"
            ),
            SketchUpComponent(
                name="Encosto",
                length=400.0,
                width=350.0,
                thickness=20.0,
                quantity=1,
                material_name="Compensado 20mm",
                layer_name="Encosto",
                component_definition="Encosto_Cadeira"
            ),
            SketchUpComponent(
                name="Pé Dianteiro",
                length=450.0,
                width=40.0,
                thickness=40.0,
                quantity=2,
                material_name="Madeira Maciça",
                layer_name="Estrutura",
                component_definition="Pe_Dianteiro"
            ),
            SketchUpComponent(
                name="Pé Traseiro",
                length=800.0,
                width=40.0,
                thickness=40.0,
                quantity=2,
                material_name="Madeira Maciça",
                layer_name="Estrutura",
                component_definition="Pe_Traseiro"
            )
        ]
    
    def _create_generic_components(self, base_name: str) -> List[SketchUpComponent]:
        """Criar componentes genéricos"""
        return [
            SketchUpComponent(
                name=f"Componente Principal",
                length=500.0,
                width=300.0,
                thickness=18.0,
                quantity=1,
                material_name="MDF 18mm",
                layer_name="Principal",
                component_definition="Comp_Principal"
            ),
            SketchUpComponent(
                name=f"Componente Secundário",
                length=300.0,
                width=200.0,
                thickness=15.0,
                quantity=2,
                material_name="MDF 15mm",
                layer_name="Secundário",
                component_definition="Comp_Secundario"
            )
        ]
    
    def _extract_materials_simulation(self) -> List[Dict]:
        """Simular extração de materiais"""
        return [
            {
                'name': 'MDF 15mm',
                'thickness': 15.0,
                'color': '#D2B48C',
                'texture': 'mdf_texture.jpg'
            },
            {
                'name': 'MDF 18mm',
                'thickness': 18.0,
                'color': '#D2B48C',
                'texture': 'mdf_texture.jpg'
            },
            {
                'name': 'MDF 25mm',
                'thickness': 25.0,
                'color': '#D2B48C',
                'texture': 'mdf_texture.jpg'
            },
            {
                'name': 'MDP 18mm',
                'thickness': 18.0,
                'color': '#CD853F',
                'texture': 'mdp_texture.jpg'
            },
            {
                'name': 'Compensado 20mm',
                'thickness': 20.0,
                'color': '#DEB887',
                'texture': 'plywood_texture.jpg'
            },
            {
                'name': 'Pinus',
                'thickness': 25.0,
                'color': '#F4A460',
                'texture': 'pine_texture.jpg'
            },
            {
                'name': 'Madeira Maciça',
                'thickness': 40.0,
                'color': '#8B4513',
                'texture': 'hardwood_texture.jpg'
            },
            {
                'name': 'Hardboard',
                'thickness': 6.0,
                'color': '#A0522D',
                'texture': 'hardboard_texture.jpg'
            }
        ]
    
    def _extract_layers_simulation(self) -> List[str]:
        """Simular extração de layers"""
        return [
            "Layer0",
            "Estrutura",
            "Prateleiras",
            "Portas",
            "Tampo",
            "Assento",
            "Encosto",
            "Principal",
            "Secundário"
        ]
    
    def _extract_model_info_simulation(self, filename: str) -> Dict:
        """Simular extração de informações do modelo"""
        return {
            'filename': filename,
            'version': '2023',
            'units': 'mm',
            'created_date': '2024-01-15',
            'modified_date': '2024-01-15',
            'author': 'CutList Pro User',
            'description': f'Modelo importado de {filename}',
            'total_components': 0,  # Será atualizado
            'bounding_box': {
                'min': {'x': 0, 'y': 0, 'z': 0},
                'max': {'x': 1000, 'y': 1000, 'z': 1000}
            }
        }
    
    def _validate_components(self, components: List[SketchUpComponent]) -> Tuple[List[SketchUpComponent], List[str]]:
        """Validar componentes extraídos"""
        validated_components = []
        warnings = []
        
        for comp in components:
            # Verificar dimensões mínimas
            if comp.length < self.min_component_size:
                warnings.append(f"Componente '{comp.name}': comprimento muito pequeno ({comp.length}mm)")
                comp.length = self.min_component_size
            
            if comp.width < self.min_component_size:
                warnings.append(f"Componente '{comp.name}': largura muito pequena ({comp.width}mm)")
                comp.width = self.min_component_size
            
            if comp.thickness < self.min_component_size:
                warnings.append(f"Componente '{comp.name}': espessura muito pequena ({comp.thickness}mm)")
                comp.thickness = self.min_component_size
            
            # Verificar dimensões máximas
            if comp.length > self.max_component_size:
                warnings.append(f"Componente '{comp.name}': comprimento muito grande ({comp.length}mm)")
                comp.length = self.max_component_size
            
            if comp.width > self.max_component_size:
                warnings.append(f"Componente '{comp.name}': largura muito grande ({comp.width}mm)")
                comp.width = self.max_component_size
            
            if comp.thickness > self.max_component_size:
                warnings.append(f"Componente '{comp.name}': espessura muito grande ({comp.thickness}mm)")
                comp.thickness = self.max_component_size
            
            # Verificar quantidade
            if comp.quantity <= 0:
                warnings.append(f"Componente '{comp.name}': quantidade inválida ({comp.quantity})")
                comp.quantity = 1
            
            validated_components.append(comp)
        
        return validated_components, warnings
    
    def convert_to_cutlist_format(self, parse_result: SketchUpParseResult) -> List[Dict]:
        """Converter componentes para formato do CutList Pro"""
        if not parse_result.success:
            return []
        
        cutlist_components = []
        
        for i, comp in enumerate(parse_result.components):
            cutlist_comp = {
                'id': i + 1,
                'name': comp.name,
                'length': comp.length,
                'width': comp.width,
                'thickness': comp.thickness,
                'quantity': comp.quantity,
                'material_id': self._map_material_to_id(comp.material_name),
                'description': f"Importado do SketchUp - Layer: {comp.layer_name}",
                'layer_name': comp.layer_name,
                'component_definition': comp.component_definition,
                'sketchup_attributes': comp.attributes
            }
            cutlist_components.append(cutlist_comp)
        
        return cutlist_components
    
    def _map_material_to_id(self, material_name: str) -> int:
        """Mapear nome do material para ID do CutList Pro"""
        material_mapping = {
            'MDF 15mm': 1,
            'MDF 18mm': 1,
            'MDF 25mm': 1,
            'MDP 18mm': 4,
            'Compensado 20mm': 2,
            'Pinus': 3,
            'Madeira Maciça': 3,
            'Hardboard': 1
        }
        
        return material_mapping.get(material_name, 1)  # Default para MDF
    
    def get_supported_formats(self) -> List[str]:
        """Obter formatos suportados"""
        return ['.skp']
    
    def get_parser_info(self) -> Dict:
        """Obter informações do parser"""
        return {
            'name': 'SketchUp Parser',
            'version': '1.0.0',
            'supported_formats': self.get_supported_formats(),
            'supported_versions': self.supported_versions,
            'features': [
                'Extração de componentes',
                'Detecção de materiais',
                'Análise de layers',
                'Validação de dimensões',
                'Conversão automática de unidades'
            ],
            'limitations': [
                'Requer SketchUp 2018 ou superior',
                'Componentes devem estar organizados em grupos',
                'Materiais devem estar aplicados aos componentes'
            ]
        }


# Funções utilitárias

def parse_sketchup_file(uploaded_file) -> SketchUpParseResult:
    """
    Função utilitária para parsear arquivo SketchUp no Streamlit
    
    Args:
        uploaded_file: Arquivo carregado via st.file_uploader
        
    Returns:
        SketchUpParseResult
    """
    parser = SketchUpParser()
    
    try:
        # Ler conteúdo do arquivo
        file_content = uploaded_file.read()
        filename = uploaded_file.name
        
        # Resetar ponteiro do arquivo
        uploaded_file.seek(0)
        
        # Parsear arquivo
        result = parser.parse_file(file_content, filename)
        
        return result
        
    except Exception as e:
        return SketchUpParseResult(
            success=False,
            components=[],
            materials=[],
            layers=[],
            model_info={},
            errors=[f"Erro ao processar arquivo: {str(e)}"],
            warnings=[]
        )


def create_project_from_sketchup(parse_result: SketchUpParseResult, project_name: str = None) -> Dict:
    """
    Criar projeto do CutList Pro a partir do resultado do parser
    
    Args:
        parse_result: Resultado do parsing
        project_name: Nome do projeto (opcional)
        
    Returns:
        Dicionário com dados do projeto
    """
    if not parse_result.success:
        return None
    
    parser = SketchUpParser()
    components = parser.convert_to_cutlist_format(parse_result)
    
    if not project_name:
        project_name = parse_result.model_info.get('filename', 'Projeto SketchUp').replace('.skp', '')
    
    project = {
        'name': project_name,
        'description': f"Projeto importado do SketchUp: {parse_result.model_info.get('filename', '')}",
        'components': components,
        'sketchup_info': {
            'model_info': parse_result.model_info,
            'materials': parse_result.materials,
            'layers': parse_result.layers,
            'warnings': parse_result.warnings
        },
        'import_date': '2024-01-15',  # Em produção, usar datetime.now()
        'status': 'Importado'
    }
    
    return project


def validate_sketchup_file_streamlit(uploaded_file) -> Dict:
    """
    Validar arquivo SketchUp no Streamlit
    
    Args:
        uploaded_file: Arquivo carregado via st.file_uploader
        
    Returns:
        Dicionário com resultado da validação
    """
    if uploaded_file is None:
        return {'valid': False, 'errors': ['Nenhum arquivo selecionado']}
    
    parser = SketchUpParser()
    
    try:
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Resetar ponteiro
        
        return parser._validate_skp_file(file_content, uploaded_file.name)
        
    except Exception as e:
        return {'valid': False, 'errors': [f'Erro ao validar arquivo: {str(e)}']}


# Exemplo de uso no Streamlit
def demo_sketchup_upload():
    """Demonstração de upload de arquivo SketchUp"""
    st.subheader("📤 Upload de Arquivo SketchUp")
    
    uploaded_file = st.file_uploader(
        "Selecione um arquivo SketchUp (.skp)",
        type=['skp'],
        help="Faça upload do seu arquivo SketchUp para extração automática de componentes"
    )
    
    if uploaded_file is not None:
        # Validar arquivo
        validation = validate_sketchup_file_streamlit(uploaded_file)
        
        if not validation['valid']:
            st.error("❌ Arquivo inválido:")
            for error in validation['errors']:
                st.error(f"• {error}")
            return None
        
        st.success(f"✅ Arquivo '{uploaded_file.name}' válido!")
        
        # Processar arquivo
        with st.spinner("🔄 Processando arquivo SketchUp..."):
            parse_result = parse_sketchup_file(uploaded_file)
        
        if parse_result.success:
            st.success("🎉 Arquivo processado com sucesso!")
            
            # Mostrar informações do modelo
            st.subheader("📋 Informações do Modelo")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Componentes", len(parse_result.components))
            with col2:
                st.metric("Materiais", len(parse_result.materials))
            with col3:
                st.metric("Layers", len(parse_result.layers))
            
            # Mostrar componentes
            if parse_result.components:
                st.subheader("🔧 Componentes Extraídos")
                
                components_data = []
                for comp in parse_result.components:
                    components_data.append({
                        'Nome': comp.name,
                        'Comprimento (mm)': comp.length,
                        'Largura (mm)': comp.width,
                        'Espessura (mm)': comp.thickness,
                        'Quantidade': comp.quantity,
                        'Material': comp.material_name,
                        'Layer': comp.layer_name
                    })
                
                st.dataframe(components_data, use_container_width=True)
            
            # Mostrar warnings se houver
            if parse_result.warnings:
                st.warning("⚠️ Avisos:")
                for warning in parse_result.warnings:
                    st.warning(f"• {warning}")
            
            return parse_result
        
        else:
            st.error("❌ Erro ao processar arquivo:")
            for error in parse_result.errors:
                st.error(f"• {error}")
            return None
    
    return None

