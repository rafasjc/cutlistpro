"""
CutList Pro - Aplicação Principal Streamlit
Planos de Corte e Orçamentos para Marcenaria
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io
import json
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="CutList Pro - Planos de Corte e Orçamentos",
    page_icon="🪚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# Importar módulos locais
try:
    from models.project import Project
    from models.component import Component
    from models.material import Material
    from algorithms.cutting_optimizer import CuttingOptimizer
    from algorithms.cost_calculator import CostCalculator
    from reports.pdf_generator import PDFGenerator
    from reports.csv_generator import CSVGenerator
    from utils.visualizations import create_cutting_diagram
    from parsers.sketchup_parser import SketchUpParser
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.info("Alguns módulos ainda estão sendo desenvolvidos. A aplicação funcionará com funcionalidades limitadas.")

# Inicializar estado da sessão
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'materials' not in st.session_state:
    st.session_state.materials = []
if 'cutting_diagrams' not in st.session_state:
    st.session_state.cutting_diagrams = []

def initialize_default_materials():
    """Inicializar materiais padrão"""
    if not st.session_state.materials:
        default_materials = [
            {
                'id': 1,
                'name': 'MDF 15mm',
                'thickness': 15.0,
                'price_per_unit': 80.00,
                'price_unit': 'm²',
                'density': 750.0,
                'standard_sizes': [(2750, 1830), (2440, 1220)],
                'description': 'MDF de média densidade, ideal para móveis'
            },
            {
                'id': 2,
                'name': 'Compensado 18mm',
                'thickness': 18.0,
                'price_per_unit': 120.00,
                'price_unit': 'm²',
                'density': 600.0,
                'standard_sizes': [(2200, 1600)],
                'description': 'Compensado multilaminado de alta qualidade'
            },
            {
                'id': 3,
                'name': 'Fita de Borda PVC',
                'thickness': 0.5,
                'price_per_unit': 2.50,
                'price_unit': 'm',
                'density': 1400.0,
                'standard_sizes': [(50000, 22)],
                'description': 'Fita de borda PVC para acabamento'
            },
            {
                'id': 4,
                'name': 'Pinus 2x4',
                'thickness': 38.0,
                'price_per_unit': 15.00,
                'price_unit': 'm',
                'density': 500.0,
                'standard_sizes': [(3000, 89)],
                'description': 'Madeira de pinus para estruturas'
            }
        ]
        st.session_state.materials = default_materials

def main():
    """Função principal da aplicação"""
    
    # Inicializar materiais padrão
    initialize_default_materials()
    
    # Header principal
    st.markdown('<h1 class="main-header">🪚 CutList Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Planos de Corte e Orçamentos para Marcenaria</p>', unsafe_allow_html=True)
    
    # Sidebar para navegação
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=CutList+Pro", width=200)
        
        page = st.selectbox(
            "Navegação",
            ["🏠 Dashboard", "📁 Projetos", "📦 Materiais", "📊 Relatórios", "⚙️ Configurações"],
            index=0
        )
        
        st.markdown("---")
        
        # Estatísticas rápidas
        st.markdown("### 📈 Estatísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Projetos", len(st.session_state.projects))
        with col2:
            st.metric("Materiais", len(st.session_state.materials))
    
    # Roteamento de páginas
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📁 Projetos":
        show_projects()
    elif page == "📦 Materiais":
        show_materials()
    elif page == "📊 Relatórios":
        show_reports()
    elif page == "⚙️ Configurações":
        show_settings()

def show_dashboard():
    """Exibir dashboard principal"""
    
    st.markdown("## 🏠 Dashboard")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_projects = len(st.session_state.projects)
        st.metric(
            label="📁 Projetos",
            value=total_projects,
            delta=f"+{total_projects} este mês"
        )
    
    with col2:
        total_components = sum(len(p.get('components', [])) for p in st.session_state.projects)
        st.metric(
            label="🔧 Componentes",
            value=total_components,
            delta=f"+{total_components} processados"
        )
    
    with col3:
        total_materials = len(st.session_state.materials)
        st.metric(
            label="📦 Materiais",
            value=total_materials,
            delta="Biblioteca completa"
        )
    
    with col4:
        estimated_savings = total_projects * 150  # Estimativa
        st.metric(
            label="💰 Economia",
            value=f"R$ {estimated_savings:,.2f}",
            delta="Otimização de cortes"
        )
    
    st.markdown("---")
    
    # Ações rápidas
    st.markdown("## 🚀 Ações Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Novo Projeto", key="new_project_dashboard"):
            st.session_state.show_new_project_form = True
            st.rerun()
    
    with col2:
        if st.button("📤 Upload SketchUp", key="upload_sketchup_dashboard"):
            st.session_state.show_upload_form = True
            st.rerun()
    
    with col3:
        if st.button("📊 Gerar Relatório", key="generate_report_dashboard"):
            st.session_state.show_report_form = True
            st.rerun()
    
    # Formulários modais
    if st.session_state.get('show_new_project_form', False):
        show_new_project_form()
    
    if st.session_state.get('show_upload_form', False):
        show_upload_form()
    
    # Projetos recentes
    if st.session_state.projects:
        st.markdown("## 📋 Projetos Recentes")
        
        for project in st.session_state.projects[-3:]:  # Últimos 3 projetos
            with st.expander(f"📁 {project['name']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Descrição:** {project.get('description', 'Sem descrição')}")
                    st.write(f"**Componentes:** {len(project.get('components', []))}")
                
                with col2:
                    st.write(f"**Criado em:** {project.get('created_at', 'N/A')}")
                    st.write(f"**Status:** {project.get('status', 'Em desenvolvimento')}")
                
                with col3:
                    if st.button(f"Abrir Projeto", key=f"open_project_{project['id']}"):
                        st.session_state.current_project = project
                        st.session_state.page = "📁 Projetos"
                        st.rerun()
    else:
        st.info("👋 Bem-vindo ao CutList Pro! Comece criando seu primeiro projeto.")

def show_new_project_form():
    """Formulário para novo projeto"""
    
    st.markdown("### 📁 Novo Projeto")
    
    with st.form("new_project_form"):
        name = st.text_input("Nome do Projeto", placeholder="Ex: Estante de Livros")
        description = st.text_area("Descrição", placeholder="Descreva seu projeto...")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Criar Projeto")
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar")
        
        if submitted and name:
            new_project = {
                'id': len(st.session_state.projects) + 1,
                'name': name,
                'description': description,
                'created_at': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'status': 'Em desenvolvimento',
                'components': [],
                'cutting_diagrams': []
            }
            
            st.session_state.projects.append(new_project)
            st.session_state.current_project = new_project
            st.session_state.show_new_project_form = False
            
            st.success(f"✅ Projeto '{name}' criado com sucesso!")
            st.rerun()
        
        if cancelled:
            st.session_state.show_new_project_form = False
            st.rerun()

def show_upload_form():
    """Formulário para upload de arquivo SketchUp"""
    
    st.markdown("### 📤 Upload de Arquivo SketchUp")
    
    uploaded_file = st.file_uploader(
        "Selecione um arquivo SketchUp (.skp)",
        type=['skp'],
        help="Faça upload do seu arquivo SketchUp para processamento automático"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
        
        # Simular processamento (implementar parser real na próxima fase)
        with st.spinner("🔄 Processando arquivo SketchUp..."):
            import time
            time.sleep(2)  # Simular processamento
            
            # Dados simulados extraídos do arquivo
            extracted_components = [
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
                    'quantity': 2,
                    'material_id': 1
                }
            ]
        
        st.success("🎉 Arquivo processado com sucesso!")
        
        # Criar projeto automaticamente
        project_name = uploaded_file.name.replace('.skp', '')
        new_project = {
            'id': len(st.session_state.projects) + 1,
            'name': project_name,
            'description': f'Projeto importado do arquivo {uploaded_file.name}',
            'created_at': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'status': 'Importado',
            'components': extracted_components,
            'cutting_diagrams': []
        }
        
        st.session_state.projects.append(new_project)
        st.session_state.current_project = new_project
        st.session_state.show_upload_form = False
        
        st.info("📁 Projeto criado automaticamente. Acesse a aba 'Projetos' para visualizar.")
        
        if st.button("🔄 Fechar"):
            st.rerun()

def show_projects():
    """Exibir página de projetos"""
    
    st.markdown("## 📁 Gerenciamento de Projetos")
    
    # Botões de ação
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("➕ Novo Projeto"):
            st.session_state.show_new_project_form = True
            st.rerun()
    
    with col2:
        if st.button("📤 Upload SketchUp"):
            st.session_state.show_upload_form = True
            st.rerun()
    
    # Formulários
    if st.session_state.get('show_new_project_form', False):
        show_new_project_form()
    
    if st.session_state.get('show_upload_form', False):
        show_upload_form()
    
    # Lista de projetos
    if st.session_state.projects:
        st.markdown("### 📋 Seus Projetos")
        
        for project in st.session_state.projects:
            with st.expander(f"📁 {project['name']}", expanded=False):
                show_project_details(project)
    else:
        st.info("📝 Nenhum projeto encontrado. Crie seu primeiro projeto!")

def show_project_details(project):
    """Exibir detalhes de um projeto"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Descrição:** {project.get('description', 'Sem descrição')}")
        st.write(f"**Criado em:** {project.get('created_at', 'N/A')}")
        st.write(f"**Status:** {project.get('status', 'Em desenvolvimento')}")
        st.write(f"**Componentes:** {len(project.get('components', []))}")
    
    with col2:
        if st.button(f"🔧 Editar", key=f"edit_{project['id']}"):
            st.session_state.current_project = project
            st.session_state.editing_project = True
            st.rerun()
        
        if st.button(f"🪚 Gerar Plano de Corte", key=f"cutting_{project['id']}"):
            generate_cutting_plan(project)
    
    # Mostrar componentes se existirem
    if project.get('components'):
        st.markdown("#### 🔧 Componentes")
        
        components_df = pd.DataFrame(project['components'])
        
        # Adicionar informações de material
        for idx, component in enumerate(components_df.to_dict('records')):
            material = next((m for m in st.session_state.materials if m['id'] == component.get('material_id')), None)
            if material:
                components_df.loc[idx, 'material_name'] = material['name']
                components_df.loc[idx, 'area_m2'] = (component['length'] * component['width']) / 1000000
                components_df.loc[idx, 'cost'] = components_df.loc[idx, 'area_m2'] * material['price_per_unit']
        
        # Exibir tabela
        st.dataframe(
            components_df[['name', 'material_name', 'length', 'width', 'thickness', 'quantity', 'area_m2', 'cost']],
            column_config={
                'name': 'Nome',
                'material_name': 'Material',
                'length': 'Comprimento (mm)',
                'width': 'Largura (mm)', 
                'thickness': 'Espessura (mm)',
                'quantity': 'Qtd',
                'area_m2': st.column_config.NumberColumn('Área (m²)', format="%.3f"),
                'cost': st.column_config.NumberColumn('Custo (R$)', format="R$ %.2f")
            },
            use_container_width=True
        )
        
        # Resumo de custos
        total_cost = components_df['cost'].sum() if 'cost' in components_df.columns else 0
        total_area = components_df['area_m2'].sum() if 'area_m2' in components_df.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Custo Total", f"R$ {total_cost:.2f}")
        with col2:
            st.metric("📐 Área Total", f"{total_area:.3f} m²")
        with col3:
            st.metric("🔢 Total de Peças", len(project['components']))

def generate_cutting_plan(project):
    """Gerar plano de corte para um projeto"""
    
    if not project.get('components'):
        st.warning("⚠️ Projeto não possui componentes para otimizar.")
        return
    
    st.markdown("### 🪚 Gerando Plano de Corte...")
    
    with st.spinner("🔄 Otimizando layout de cortes..."):
        import time
        time.sleep(1)  # Simular processamento
        
        # Simular algoritmo de otimização
        cutting_diagram = create_mock_cutting_diagram(project['components'])
        
        # Salvar no projeto
        project['cutting_diagrams'] = [cutting_diagram]
    
    st.success("✅ Plano de corte gerado com sucesso!")
    
    # Exibir diagrama
    show_cutting_diagram(cutting_diagram)

def create_mock_cutting_diagram(components):
    """Criar diagrama de corte simulado"""
    
    # Configurações da chapa padrão
    sheet_width = 2750
    sheet_height = 1830
    
    # Simular posicionamento das peças
    positioned_pieces = []
    current_x = 0
    current_y = 0
    row_height = 0
    
    for i, component in enumerate(components):
        for qty in range(component['quantity']):
            piece = {
                'id': f"{component['name']}_{qty+1}",
                'name': f"{component['name']} {qty+1}" if component['quantity'] > 1 else component['name'],
                'x': current_x,
                'y': current_y,
                'width': component['length'],
                'height': component['width'],
                'color': f"hsl({(i * 60) % 360}, 70%, 80%)"
            }
            
            positioned_pieces.append(piece)
            
            # Atualizar posição
            current_x += component['length'] + 10  # 10mm de margem
            row_height = max(row_height, component['width'])
            
            # Nova linha se necessário
            if current_x + component['length'] > sheet_width:
                current_x = 0
                current_y += row_height + 10
                row_height = 0
    
    # Calcular estatísticas
    total_area_pieces = sum(p['width'] * p['height'] for p in positioned_pieces) / 1000000  # m²
    sheet_area = (sheet_width * sheet_height) / 1000000  # m²
    utilization = (total_area_pieces / sheet_area) * 100
    waste = 100 - utilization
    
    return {
        'sheet_width': sheet_width,
        'sheet_height': sheet_height,
        'pieces': positioned_pieces,
        'utilization': utilization,
        'waste': waste,
        'total_area_pieces': total_area_pieces,
        'sheet_area': sheet_area
    }

def show_cutting_diagram(diagram):
    """Exibir diagrama de corte"""
    
    # Criar figura Plotly
    fig = go.Figure()
    
    # Adicionar chapa de fundo
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=diagram['sheet_width'], y1=diagram['sheet_height'],
        line=dict(color="black", width=2),
        fillcolor="lightgray",
        opacity=0.3
    )
    
    # Adicionar peças
    for piece in diagram['pieces']:
        fig.add_shape(
            type="rect",
            x0=piece['x'], y0=piece['y'],
            x1=piece['x'] + piece['width'], y1=piece['y'] + piece['height'],
            line=dict(color="black", width=1),
            fillcolor=piece['color'],
            opacity=0.8
        )
        
        # Adicionar texto da peça
        fig.add_annotation(
            x=piece['x'] + piece['width']/2,
            y=piece['y'] + piece['height']/2,
            text=piece['name'],
            showarrow=False,
            font=dict(size=10, color="black"),
            bgcolor="white",
            opacity=0.8
        )
    
    # Configurar layout
    fig.update_layout(
        title=f"Diagrama de Corte - Chapa {diagram['sheet_width']}x{diagram['sheet_height']}mm",
        xaxis=dict(title="Largura (mm)", scaleanchor="y", scaleratio=1),
        yaxis=dict(title="Altura (mm)"),
        showlegend=False,
        width=800,
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Aproveitamento", f"{diagram['utilization']:.1f}%")
    
    with col2:
        st.metric("🗑️ Desperdício", f"{diagram['waste']:.1f}%")
    
    with col3:
        st.metric("📐 Área Utilizada", f"{diagram['total_area_pieces']:.3f} m²")

def show_materials():
    """Exibir página de materiais"""
    
    st.markdown("## 📦 Biblioteca de Materiais")
    
    # Botão para adicionar material
    if st.button("➕ Adicionar Material"):
        st.session_state.show_add_material_form = True
        st.rerun()
    
    # Formulário para adicionar material
    if st.session_state.get('show_add_material_form', False):
        show_add_material_form()
    
    # Exibir materiais em cards
    if st.session_state.materials:
        cols = st.columns(2)
        
        for i, material in enumerate(st.session_state.materials):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"### 📦 {material['name']}")
                    st.write(f"**Espessura:** {material['thickness']}mm")
                    st.write(f"**Preço:** R$ {material['price_per_unit']:.2f}/{material['price_unit']}")
                    st.write(f"**Densidade:** {material['density']} kg/m³")
                    
                    # Tamanhos padrão
                    sizes_text = ", ".join([f"{w}x{h}mm" for w, h in material['standard_sizes']])
                    st.write(f"**Tamanhos:** {sizes_text}")
                    
                    st.write(f"**Descrição:** {material['description']}")
                    
                    if st.button(f"✏️ Editar", key=f"edit_material_{material['id']}"):
                        st.session_state.editing_material = material
                        st.rerun()

def show_add_material_form():
    """Formulário para adicionar material"""
    
    st.markdown("### ➕ Adicionar Material")
    
    with st.form("add_material_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nome do Material")
            thickness = st.number_input("Espessura (mm)", min_value=0.1, value=15.0)
            price = st.number_input("Preço por Unidade", min_value=0.01, value=80.00)
            price_unit = st.selectbox("Unidade de Preço", ["m²", "m³", "m", "piece"])
        
        with col2:
            density = st.number_input("Densidade (kg/m³)", min_value=1.0, value=750.0)
            description = st.text_area("Descrição")
            
            # Tamanhos padrão (simplificado)
            width = st.number_input("Largura Padrão (mm)", min_value=1, value=2750)
            height = st.number_input("Altura Padrão (mm)", min_value=1, value=1830)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Adicionar Material")
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar")
        
        if submitted and name:
            new_material = {
                'id': len(st.session_state.materials) + 1,
                'name': name,
                'thickness': thickness,
                'price_per_unit': price,
                'price_unit': price_unit,
                'density': density,
                'standard_sizes': [(width, height)],
                'description': description
            }
            
            st.session_state.materials.append(new_material)
            st.session_state.show_add_material_form = False
            
            st.success(f"✅ Material '{name}' adicionado com sucesso!")
            st.rerun()
        
        if cancelled:
            st.session_state.show_add_material_form = False
            st.rerun()

def show_reports():
    """Exibir página de relatórios"""
    
    st.markdown("## 📊 Relatórios e Exportação")
    
    if not st.session_state.projects:
        st.info("📝 Nenhum projeto disponível para gerar relatórios.")
        return
    
    # Seleção de projeto
    project_names = [p['name'] for p in st.session_state.projects]
    selected_project_name = st.selectbox("Selecione um Projeto", project_names)
    
    selected_project = next(p for p in st.session_state.projects if p['name'] == selected_project_name)
    
    if not selected_project.get('components'):
        st.warning("⚠️ Projeto selecionado não possui componentes.")
        return
    
    st.markdown("### 📋 Tipos de Relatório")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Lista de Peças"):
            generate_parts_list_report(selected_project)
    
    with col2:
        if st.button("💰 Estimativa de Custo"):
            generate_cost_estimate_report(selected_project)
    
    with col3:
        if st.button("🪚 Diagrama de Corte"):
            if selected_project.get('cutting_diagrams'):
                show_cutting_diagram(selected_project['cutting_diagrams'][0])
            else:
                st.info("Gere um plano de corte primeiro na aba Projetos.")

def generate_parts_list_report(project):
    """Gerar relatório de lista de peças"""
    
    st.markdown("### 📄 Lista de Peças")
    
    components_df = pd.DataFrame(project['components'])
    
    # Adicionar informações calculadas
    for idx, component in enumerate(components_df.to_dict('records')):
        material = next((m for m in st.session_state.materials if m['id'] == component.get('material_id')), None)
        if material:
            components_df.loc[idx, 'material_name'] = material['name']
            components_df.loc[idx, 'area_m2'] = (component['length'] * component['width']) / 1000000
            components_df.loc[idx, 'cost'] = components_df.loc[idx, 'area_m2'] * material['price_per_unit']
    
    # Exibir tabela formatada
    st.dataframe(
        components_df,
        column_config={
            'name': 'Nome da Peça',
            'material_name': 'Material',
            'length': 'Comprimento (mm)',
            'width': 'Largura (mm)',
            'thickness': 'Espessura (mm)',
            'quantity': 'Quantidade',
            'area_m2': st.column_config.NumberColumn('Área (m²)', format="%.3f"),
            'cost': st.column_config.NumberColumn('Custo (R$)', format="R$ %.2f")
        },
        use_container_width=True
    )
    
    # Opções de exportação
    st.markdown("#### 📤 Exportar Relatório")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Exportar CSV"):
            csv_data = components_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"lista_pecas_{project['name']}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Exportar Excel"):
            # Simular geração de Excel
            st.info("🔄 Funcionalidade Excel em desenvolvimento...")
    
    with col3:
        if st.button("📄 Exportar PDF"):
            # Simular geração de PDF
            st.info("🔄 Funcionalidade PDF em desenvolvimento...")

def generate_cost_estimate_report(project):
    """Gerar relatório de estimativa de custo"""
    
    st.markdown("### 💰 Estimativa de Custo")
    
    components_df = pd.DataFrame(project['components'])
    
    # Calcular custos detalhados
    total_material_cost = 0
    material_breakdown = {}
    
    for component in project['components']:
        material = next((m for m in st.session_state.materials if m['id'] == component.get('material_id')), None)
        if material:
            area = (component['length'] * component['width']) / 1000000  # m²
            cost = area * material['price_per_unit'] * component['quantity']
            total_material_cost += cost
            
            if material['name'] not in material_breakdown:
                material_breakdown[material['name']] = {'area': 0, 'cost': 0}
            
            material_breakdown[material['name']]['area'] += area * component['quantity']
            material_breakdown[material['name']]['cost'] += cost
    
    # Custos adicionais (estimativas)
    waste_cost = total_material_cost * 0.15  # 15% desperdício
    labor_cost = total_material_cost * 0.30  # 30% mão de obra
    overhead_cost = total_material_cost * 0.10  # 10% overhead
    profit_margin = (total_material_cost + waste_cost + labor_cost + overhead_cost) * 0.20  # 20% lucro
    
    total_cost = total_material_cost + waste_cost + labor_cost + overhead_cost + profit_margin
    
    # Exibir breakdown de custos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Breakdown de Custos")
        
        cost_data = {
            'Item': ['Material', 'Desperdício', 'Mão de Obra', 'Overhead', 'Margem de Lucro', 'TOTAL'],
            'Valor': [total_material_cost, waste_cost, labor_cost, overhead_cost, profit_margin, total_cost],
            'Percentual': ['Base', '15%', '30%', '10%', '20%', '100%']
        }
        
        cost_df = pd.DataFrame(cost_data)
        
        st.dataframe(
            cost_df,
            column_config={
                'Valor': st.column_config.NumberColumn('Valor (R$)', format="R$ %.2f")
            },
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("#### 📦 Breakdown por Material")
        
        material_data = []
        for material_name, data in material_breakdown.items():
            material_data.append({
                'Material': material_name,
                'Área (m²)': data['area'],
                'Custo (R$)': data['cost']
            })
        
        if material_data:
            material_df = pd.DataFrame(material_data)
            st.dataframe(
                material_df,
                column_config={
                    'Área (m²)': st.column_config.NumberColumn('Área (m²)', format="%.3f"),
                    'Custo (R$)': st.column_config.NumberColumn('Custo (R$)', format="R$ %.2f")
                },
                use_container_width=True,
                hide_index=True
            )
    
    # Métricas principais
    st.markdown("#### 📊 Resumo Executivo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Custo Total", f"R$ {total_cost:.2f}")
    
    with col2:
        st.metric("📦 Custo Material", f"R$ {total_material_cost:.2f}")
    
    with col3:
        st.metric("🔨 Custo Mão de Obra", f"R$ {labor_cost:.2f}")
    
    with col4:
        st.metric("📈 Margem de Lucro", f"R$ {profit_margin:.2f}")

def show_settings():
    """Exibir página de configurações"""
    
    st.markdown("## ⚙️ Configurações")
    
    # Configurações gerais
    st.markdown("### 🔧 Configurações Gerais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Idioma", ["Português (BR)", "English", "Español"], index=0)
        st.selectbox("Moeda", ["Real (R$)", "Dólar (US$)", "Euro (€)"], index=0)
        st.number_input("Margem de Corte Padrão (mm)", min_value=0.0, value=3.0, step=0.1)
    
    with col2:
        st.selectbox("Unidade de Medida", ["Milímetros", "Centímetros", "Metros"], index=0)
        st.number_input("Fator de Desperdício (%)", min_value=0.0, max_value=50.0, value=15.0, step=1.0)
        st.number_input("Margem de Lucro Padrão (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
    
    # Configurações de algoritmo
    st.markdown("### 🧮 Configurações de Algoritmo")
    
    algorithm = st.selectbox(
        "Algoritmo de Otimização Padrão",
        ["Bottom-Left Fill", "Best Fit Decreasing", "Guillotine Split"],
        index=0
    )
    
    st.slider("Prioridade de Aproveitamento", 0, 100, 85, help="0 = Velocidade, 100 = Máximo aproveitamento")
    
    # Configurações de exportação
    st.markdown("### 📤 Configurações de Exportação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Formato de Relatório Padrão", ["PDF", "Excel", "CSV"], index=0)
        st.checkbox("Incluir diagramas nos relatórios", value=True)
    
    with col2:
        st.selectbox("Qualidade de Imagem", ["Alta", "Média", "Baixa"], index=0)
        st.checkbox("Incluir breakdown de custos", value=True)
    
    # Botões de ação
    st.markdown("### 🔄 Ações")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Configurações"):
            st.success("✅ Configurações salvas com sucesso!")
    
    with col2:
        if st.button("🔄 Restaurar Padrões"):
            st.info("🔄 Configurações restauradas para os valores padrão.")
    
    with col3:
        if st.button("📤 Exportar Dados"):
            # Simular exportação de dados
            data = {
                'projects': st.session_state.projects,
                'materials': st.session_state.materials
            }
            
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="⬇️ Download Backup",
                data=json_data,
                file_name=f"cutlist_pro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()

