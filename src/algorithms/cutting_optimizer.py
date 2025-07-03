"""
Algoritmos de otimização de cortes para CutList Pro
Adaptado para Streamlit
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class Rectangle:
    """Representa um retângulo para otimização"""
    id: str
    name: str
    width: float
    height: float
    quantity: int = 1
    material_id: Optional[int] = None
    priority: int = 1
    can_rotate: bool = True
    
    def get_area(self) -> float:
        """Calcular área do retângulo"""
        return self.width * self.height
    
    def fits_in(self, container_width: float, container_height: float) -> bool:
        """Verificar se cabe no container"""
        return (self.width <= container_width and self.height <= container_height) or \
               (self.can_rotate and self.height <= container_width and self.width <= container_height)


@dataclass
class PlacedRectangle:
    """Representa um retângulo posicionado"""
    rectangle: Rectangle
    x: float
    y: float
    rotated: bool = False
    
    def get_width(self) -> float:
        """Largura considerando rotação"""
        return self.rectangle.height if self.rotated else self.rectangle.width
    
    def get_height(self) -> float:
        """Altura considerando rotação"""
        return self.rectangle.width if self.rotated else self.rectangle.height
    
    def get_right(self) -> float:
        """Coordenada direita"""
        return self.x + self.get_width()
    
    def get_top(self) -> float:
        """Coordenada superior"""
        return self.y + self.get_height()
    
    def overlaps_with(self, other: 'PlacedRectangle') -> bool:
        """Verificar sobreposição com outro retângulo"""
        return not (self.get_right() <= other.x or 
                   other.get_right() <= self.x or
                   self.get_top() <= other.y or 
                   other.get_top() <= self.y)


@dataclass
class CuttingSheet:
    """Representa uma chapa para corte"""
    width: float
    height: float
    material_id: int
    thickness: float
    placed_rectangles: List[PlacedRectangle]
    kerf_width: float = 3.0  # largura do corte
    
    def __post_init__(self):
        if not hasattr(self, 'placed_rectangles'):
            self.placed_rectangles = []
    
    def get_used_area(self) -> float:
        """Calcular área utilizada"""
        return sum(rect.rectangle.get_area() for rect in self.placed_rectangles)
    
    def get_total_area(self) -> float:
        """Calcular área total da chapa"""
        return self.width * self.height
    
    def get_utilization(self) -> float:
        """Calcular percentual de utilização"""
        total_area = self.get_total_area()
        return (self.get_used_area() / total_area * 100) if total_area > 0 else 0
    
    def get_waste_percentage(self) -> float:
        """Calcular percentual de desperdício"""
        return 100 - self.get_utilization()
    
    def can_place_rectangle(self, rect: Rectangle, x: float, y: float, rotated: bool = False) -> bool:
        """Verificar se pode posicionar retângulo"""
        width = rect.height if rotated else rect.width
        height = rect.width if rotated else rect.height
        
        # Verificar limites da chapa
        if x + width > self.width or y + height > self.height:
            return False
        
        # Verificar sobreposição
        test_placed = PlacedRectangle(rect, x, y, rotated)
        for placed in self.placed_rectangles:
            if test_placed.overlaps_with(placed):
                return False
        
        return True
    
    def place_rectangle(self, rect: Rectangle, x: float, y: float, rotated: bool = False) -> bool:
        """Posicionar retângulo na chapa"""
        if self.can_place_rectangle(rect, x, y, rotated):
            placed = PlacedRectangle(rect, x, y, rotated)
            self.placed_rectangles.append(placed)
            return True
        return False
    
    def find_best_position(self, rect: Rectangle) -> Optional[Tuple[float, float, bool]]:
        """Encontrar melhor posição para o retângulo"""
        best_position = None
        best_waste = float('inf')
        
        # Tentar posições possíveis
        positions = self._generate_positions()
        
        for x, y in positions:
            # Tentar sem rotação
            if rect.can_rotate or not rect.can_rotate:
                if self.can_place_rectangle(rect, x, y, False):
                    waste = self._calculate_position_waste(rect, x, y, False)
                    if waste < best_waste:
                        best_waste = waste
                        best_position = (x, y, False)
            
            # Tentar com rotação se permitido
            if rect.can_rotate:
                if self.can_place_rectangle(rect, x, y, True):
                    waste = self._calculate_position_waste(rect, x, y, True)
                    if waste < best_waste:
                        best_waste = waste
                        best_position = (x, y, True)
        
        return best_position
    
    def _generate_positions(self) -> List[Tuple[float, float]]:
        """Gerar posições candidatas"""
        positions = [(0, 0)]  # Sempre tentar origem
        
        # Adicionar posições baseadas em retângulos existentes
        for placed in self.placed_rectangles:
            # Canto direito
            positions.append((placed.get_right() + self.kerf_width, placed.y))
            # Canto superior
            positions.append((placed.x, placed.get_top() + self.kerf_width))
            # Canto superior direito
            positions.append((placed.get_right() + self.kerf_width, placed.get_top() + self.kerf_width))
        
        # Filtrar posições válidas
        valid_positions = []
        for x, y in positions:
            if 0 <= x < self.width and 0 <= y < self.height:
                valid_positions.append((x, y))
        
        return valid_positions
    
    def _calculate_position_waste(self, rect: Rectangle, x: float, y: float, rotated: bool) -> float:
        """Calcular desperdício para uma posição específica"""
        width = rect.height if rotated else rect.width
        height = rect.width if rotated else rect.height
        
        # Calcular área desperdiçada (simplificado)
        right_waste = max(0, self.width - (x + width))
        top_waste = max(0, self.height - (y + height))
        
        return right_waste * height + top_waste * width


class CuttingOptimizer:
    """Otimizador de cortes principal"""
    
    def __init__(self, kerf_width: float = 3.0):
        self.kerf_width = kerf_width
    
    def optimize_bottom_left_fill(
        self, 
        rectangles: List[Rectangle], 
        sheet_width: float, 
        sheet_height: float,
        material_id: int,
        thickness: float
    ) -> List[CuttingSheet]:
        """
        Algoritmo Bottom-Left Fill
        Posiciona peças no canto inferior esquerdo disponível
        """
        sheets = []
        remaining_rectangles = rectangles.copy()
        
        # Ordenar por área decrescente
        remaining_rectangles.sort(key=lambda r: r.get_area(), reverse=True)
        
        while remaining_rectangles:
            sheet = CuttingSheet(sheet_width, sheet_height, material_id, thickness, [], self.kerf_width)
            
            placed_any = True
            while placed_any and remaining_rectangles:
                placed_any = False
                
                for i, rect in enumerate(remaining_rectangles):
                    position = sheet.find_best_position(rect)
                    if position:
                        x, y, rotated = position
                        if sheet.place_rectangle(rect, x, y, rotated):
                            remaining_rectangles.pop(i)
                            placed_any = True
                            break
            
            if sheet.placed_rectangles:  # Só adicionar se tiver peças
                sheets.append(sheet)
            else:
                # Se não conseguiu colocar nenhuma peça, há um problema
                break
        
        return sheets
    
    def optimize_best_fit_decreasing(
        self,
        rectangles: List[Rectangle],
        sheet_width: float,
        sheet_height: float,
        material_id: int,
        thickness: float
    ) -> List[CuttingSheet]:
        """
        Algoritmo Best Fit Decreasing
        Escolhe a posição que minimiza o desperdício
        """
        sheets = []
        remaining_rectangles = rectangles.copy()
        
        # Ordenar por área decrescente
        remaining_rectangles.sort(key=lambda r: r.get_area(), reverse=True)
        
        while remaining_rectangles:
            sheet = CuttingSheet(sheet_width, sheet_height, material_id, thickness, [], self.kerf_width)
            
            # Tentar colocar cada retângulo na melhor posição
            i = 0
            while i < len(remaining_rectangles):
                rect = remaining_rectangles[i]
                position = sheet.find_best_position(rect)
                
                if position:
                    x, y, rotated = position
                    sheet.place_rectangle(rect, x, y, rotated)
                    remaining_rectangles.pop(i)
                else:
                    i += 1
            
            if sheet.placed_rectangles:
                sheets.append(sheet)
            else:
                break
        
        return sheets
    
    def optimize_guillotine_split(
        self,
        rectangles: List[Rectangle],
        sheet_width: float,
        sheet_height: float,
        material_id: int,
        thickness: float
    ) -> List[CuttingSheet]:
        """
        Algoritmo Guillotine Split
        Divide a chapa em seções menores
        """
        sheets = []
        remaining_rectangles = rectangles.copy()
        
        # Ordenar por área decrescente
        remaining_rectangles.sort(key=lambda r: r.get_area(), reverse=True)
        
        while remaining_rectangles:
            sheet = CuttingSheet(sheet_width, sheet_height, material_id, thickness, [], self.kerf_width)
            
            # Implementação simplificada do guillotine
            self._guillotine_pack(sheet, remaining_rectangles, 0, 0, sheet_width, sheet_height)
            
            if sheet.placed_rectangles:
                sheets.append(sheet)
            else:
                break
        
        return sheets
    
    def _guillotine_pack(
        self,
        sheet: CuttingSheet,
        rectangles: List[Rectangle],
        x: float,
        y: float,
        width: float,
        height: float
    ):
        """Empacotamento recursivo guillotine"""
        if not rectangles or width <= 0 or height <= 0:
            return
        
        # Encontrar retângulo que melhor se encaixa
        best_rect = None
        best_index = -1
        best_rotated = False
        
        for i, rect in enumerate(rectangles):
            # Tentar sem rotação
            if rect.width <= width and rect.height <= height:
                if best_rect is None or rect.get_area() > best_rect.get_area():
                    best_rect = rect
                    best_index = i
                    best_rotated = False
            
            # Tentar com rotação
            if rect.can_rotate and rect.height <= width and rect.width <= height:
                if best_rect is None or rect.get_area() > best_rect.get_area():
                    best_rect = rect
                    best_index = i
                    best_rotated = True
        
        if best_rect is None:
            return
        
        # Posicionar retângulo
        sheet.place_rectangle(best_rect, x, y, best_rotated)
        rectangles.pop(best_index)
        
        # Calcular espaços restantes
        rect_width = best_rect.height if best_rotated else best_rect.width
        rect_height = best_rect.width if best_rotated else best_rect.height
        
        # Dividir espaço restante
        right_width = width - rect_width - self.kerf_width
        top_height = height - rect_height - self.kerf_width
        
        # Recursão nos espaços restantes
        if right_width > 0:
            self._guillotine_pack(
                sheet, rectangles,
                x + rect_width + self.kerf_width, y,
                right_width, rect_height
            )
        
        if top_height > 0:
            self._guillotine_pack(
                sheet, rectangles,
                x, y + rect_height + self.kerf_width,
                width, top_height
            )
    
    def optimize(
        self,
        components: List[Dict],
        sheet_width: float,
        sheet_height: float,
        material_id: int,
        thickness: float,
        algorithm: str = "bottom_left_fill"
    ) -> Dict:
        """
        Otimizar layout de cortes
        """
        # Converter componentes para retângulos
        rectangles = []
        for comp in components:
            for i in range(comp.get('quantity', 1)):
                rect = Rectangle(
                    id=f"{comp['name']}_{i+1}",
                    name=f"{comp['name']} {i+1}" if comp.get('quantity', 1) > 1 else comp['name'],
                    width=comp['length'],
                    height=comp['width'],
                    material_id=comp.get('material_id'),
                    priority=comp.get('priority', 1)
                )
                rectangles.append(rect)
        
        # Executar algoritmo selecionado
        if algorithm == "best_fit_decreasing":
            sheets = self.optimize_best_fit_decreasing(rectangles, sheet_width, sheet_height, material_id, thickness)
        elif algorithm == "guillotine_split":
            sheets = self.optimize_guillotine_split(rectangles, sheet_width, sheet_height, material_id, thickness)
        else:  # bottom_left_fill (padrão)
            sheets = self.optimize_bottom_left_fill(rectangles, sheet_width, sheet_height, material_id, thickness)
        
        # Calcular estatísticas
        total_area_pieces = sum(rect.get_area() for rect in rectangles) / 1000000  # mm² para m²
        total_area_sheets = sum(sheet.get_total_area() for sheet in sheets) / 1000000  # mm² para m²
        
        utilization = (total_area_pieces / total_area_sheets * 100) if total_area_sheets > 0 else 0
        waste = 100 - utilization
        
        # Converter para formato de saída
        cutting_diagrams = []
        for i, sheet in enumerate(sheets):
            pieces = []
            for placed in sheet.placed_rectangles:
                pieces.append({
                    'id': placed.rectangle.id,
                    'name': placed.rectangle.name,
                    'x': placed.x,
                    'y': placed.y,
                    'width': placed.get_width(),
                    'height': placed.get_height(),
                    'rotated': placed.rotated,
                    'color': f"hsl({hash(placed.rectangle.name) % 360}, 70%, 80%)"
                })
            
            cutting_diagrams.append({
                'id': i + 1,
                'sheet_width': sheet.width,
                'sheet_height': sheet.height,
                'material_id': sheet.material_id,
                'thickness': sheet.thickness,
                'pieces': pieces,
                'utilization': sheet.get_utilization(),
                'waste': sheet.get_waste_percentage(),
                'used_area': sheet.get_used_area() / 1000000,  # mm² para m²
                'total_area': sheet.get_total_area() / 1000000  # mm² para m²
            })
        
        return {
            'cutting_diagrams': cutting_diagrams,
            'summary': {
                'total_sheets': len(sheets),
                'total_area_pieces': total_area_pieces,
                'total_area_sheets': total_area_sheets,
                'overall_utilization': utilization,
                'overall_waste': waste,
                'algorithm_used': algorithm
            }
        }


# Funções utilitárias

def create_mock_cutting_diagram(components: List[Dict], sheet_width: float = 2750, sheet_height: float = 1830) -> Dict:
    """Criar diagrama de corte simulado para demonstração"""
    optimizer = CuttingOptimizer()
    
    # Usar primeiro material disponível
    material_id = components[0].get('material_id', 1) if components else 1
    thickness = components[0].get('thickness', 15.0) if components else 15.0
    
    result = optimizer.optimize(
        components=components,
        sheet_width=sheet_width,
        sheet_height=sheet_height,
        material_id=material_id,
        thickness=thickness,
        algorithm="bottom_left_fill"
    )
    
    return result['cutting_diagrams'][0] if result['cutting_diagrams'] else None


def calculate_optimization_score(cutting_diagrams: List[Dict]) -> float:
    """Calcular pontuação de otimização (0-100)"""
    if not cutting_diagrams:
        return 0
    
    total_utilization = sum(diagram['utilization'] for diagram in cutting_diagrams)
    avg_utilization = total_utilization / len(cutting_diagrams)
    
    # Penalizar pelo número de chapas
    sheet_penalty = max(0, (len(cutting_diagrams) - 1) * 5)
    
    score = max(0, avg_utilization - sheet_penalty)
    return min(100, score)


def compare_algorithms(
    components: List[Dict],
    sheet_width: float,
    sheet_height: float,
    material_id: int,
    thickness: float
) -> Dict:
    """Comparar diferentes algoritmos de otimização"""
    optimizer = CuttingOptimizer()
    algorithms = ["bottom_left_fill", "best_fit_decreasing", "guillotine_split"]
    
    results = {}
    
    for algorithm in algorithms:
        result = optimizer.optimize(
            components=components,
            sheet_width=sheet_width,
            sheet_height=sheet_height,
            material_id=material_id,
            thickness=thickness,
            algorithm=algorithm
        )
        
        results[algorithm] = {
            'summary': result['summary'],
            'score': calculate_optimization_score(result['cutting_diagrams'])
        }
    
    # Encontrar melhor algoritmo
    best_algorithm = max(results.keys(), key=lambda k: results[k]['score'])
    
    return {
        'results': results,
        'best_algorithm': best_algorithm,
        'comparison': results
    }

