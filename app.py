"""
CutList Pro - Aplicação Principal Streamlit
Geração de planos de corte e orçamentos para marcenaria
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import io
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar módulos locais
from models.project import Project, create_sample_project
from models.component import Component, create_component_from_dimensions
from models.material import Material, create_default_materials, get_material_by_id
from algorithms.cutting_optimizer import CuttingOptimizer, create_mock_cutting_diagram
from parsers.sketchup_parser import parse_sketchup_file, create_project_from_sketchup, demo_sketchup_upload


# Configuração da página
st.set_page_config(
    page_title="CutList Pro",
    page_icon="🪚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7bb8 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2e7bb8;
    }
    
    .component-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #2e7bb8 0%, #1f4e79 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7bb8 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
def init_session_state():
    """Inicializar estado da sessão"""
    if 'projects' not in st.session_state:
        st.session_state.projects = [create_sample_project()]
    
    if 'materials' not in st.session_state:
        st.session_state.materials = create_default_materials()
    
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = 1
    
    if 'cutting_diagrams' not in st.session_state:
        st.session_state.cutting_diagrams = {}

def get_current_project() -> Optional[Project]:
    """Obter projeto atual"""
    for project in st.session_state.projects:
        if project.id == st.session_state.current_project_id:
            return project
    return None

def save_project(project: Project):
    """Salvar projeto no estado da sessão"""
    for i, p in enumerate(st.session_state.projects):
        if p.id == project.id:
            st.session_state.projects[i] = project
            return
    st.session_state.projects.append(project)

def create_cutting_diagram_visualization(cutting_diagram: Dict) -> go.Figure:
    """Criar visualização do diagrama de corte"""
    fig = go.Figure()
    
    # Adicionar chapa de fundo
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=cutting_diagram['sheet_width'],
        y1=cutting_diagram['sheet_height'],
        line=dict(color="black", width=2),
        fillcolor="lightgray",
        opacity=0.3
    )
    
    # Adicionar peças
    for piece in cutting_diagram['pieces']:
        fig.add_shape(
            type="rect",
            x0=piece['x'],
            y0=piece['y'],
            x1=piece['x'] + piece['width'],
            y1=piece['y'] + piece['height'],
            line=dict(color="black", width=1),
            fillcolor=piece.get('color', '#3498db'),
            opacity=0.7
        )
        
        # Adicionar texto com nome da peça
        fig.add_annotation(
            x=piece['x'] + piece['width']/2,
            y=piece['y'] + piece['height']/2,
            text=piece['name'],
            showarrow=False,
            font=dict(size=10, color="black"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
    
    # Configurar layout
    fig.update_layout(
        title=f"Diagrama de Corte - Chapa {cutting_diagram['id']}",
        xaxis=dict(title="Largura (mm)", scaleanchor="y", scaleratio=1),
        yaxis=dict(title="Altura (mm)"),
        showlegend=False,
        width=800,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def render_dashboard():
    """Renderizar dashboard principal"""
    st.markdown('<div class="main-header"><h1>🪚 CutList Pro</h1><p>Planos de Corte e Orçamentos Profissionais</p></div>', unsafe_allow_html=True)
    
    # Estatísticas gerais
    total_projects = len(st.session_state.projects)
    total_components = sum(len(p.components) for p in st.session_state.projects)
    total_materials = len(st.session_state.materials)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Projetos", total_projects)
    
    with col2:
        st.metric("🔧 Componentes", total_components)
    
    with col3:
        st.metric("📦 Materiais", total_materials)
    
    with col4:
        current_project = get_current_project()
        if current_project:
            st.metric("📊 Projeto Atual", current_project.name)
    
    st.markdown("---")
    
    # Lista de projetos
    st.subheader("📋 Projetos Recentes")
    
    if st.session_state.projects:
        for project in st.session_state.projects[-5:]:  # Últimos 5 projetos
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{project.name}**")
                    st.caption(project.description[:100] + "..." if len(project.description) > 100 else project.description)
                
                with col2:
                    st.write(f"📅 {project.updated_at}")
                
                with col3:
                    st.write(f"🔧 {len(project.components)} componentes")
                
                with col4:
                    if st.button("Abrir", key=f"open_{project.id}"):
                        st.session_state.current_project_id = project.id
                        st.rerun()
    else:
        st.info("Nenhum projeto encontrado. Crie um novo projeto ou importe um arquivo SketchUp.")

def render_project_manager():
    """Renderizar gerenciador de projetos"""
    st.header("📁 Gerenciador de Projetos")
    
    # Seletor de projeto
    project_options = {p.id: f"{p.name} ({len(p.components)} componentes)" for p in st.session_state.projects}
    
    if project_options:
        selected_project_id = st.selectbox(
            "Selecionar Projeto:",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x],
            index=list(project_options.keys()).index(st.session_state.current_project_id) if st.session_state.current_project_id in project_options else 0
        )
        
        if selected_project_id != st.session_state.current_project_id:
            st.session_state.current_project_id = selected_project_id
            st.rerun()
    
    current_project = get_current_project()
    
    if current_project:
        # Informações do projeto
        st.subheader(f"📊 {current_project.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Descrição:** {current_project.description}")
            st.write(f"**Status:** {current_project.status}")
            st.write(f"**Criado em:** {current_project.created_at}")
        
        with col2:
            st.write(f"**Atualizado em:** {current_project.updated_at}")
            st.write(f"**Componentes:** {len(current_project.components)}")
            st.write(f"**Área Total:** {current_project.calculate_total_area():.2f} m²")
        
        st.markdown("---")
        
        # Lista de componentes
        st.subheader("🔧 Componentes")
        
        if current_project.components:
            # Criar DataFrame para exibição
            components_data = []
            for comp in current_project.components:
                material = get_material_by_id(st.session_state.materials, comp.get('material_id', 1))
                material_name = material.name if material else "Material não encontrado"
                
                components_data.append({
                    'Nome': comp['name'],
                    'Comprimento (mm)': comp['length'],
                    'Largura (mm)': comp['width'],
                    'Espessura (mm)': comp['thickness'],
                    'Quantidade': comp['quantity'],
                    'Material': material_name,
                    'Área (m²)': f"{(comp['length'] * comp['width'] * comp['quantity']) / 1000000:.3f}"
                })
            
            df = pd.DataFrame(components_data)
            st.dataframe(df, use_container_width=True)
            
            # Botões de ação
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎯 Gerar Plano de Corte", type="primary"):
                    with st.spinner("Gerando plano de corte..."):
                        # Usar primeiro material do projeto
                        first_material_id = current_project.components[0].get('material_id', 1)
                        material = get_material_by_id(st.session_state.materials, first_material_id)
                        
                        if material:
                            sheet_size = material.get_largest_sheet_size()
                            optimizer = CuttingOptimizer()
                            
                            result = optimizer.optimize(
                                components=current_project.components,
                                sheet_width=sheet_size[0],
                                sheet_height=sheet_size[1],
                                material_id=first_material_id,
                                thickness=material.thickness
                            )
                            
                            st.session_state.cutting_diagrams[current_project.id] = result
                            st.success("✅ Plano de corte gerado com sucesso!")
                            st.rerun()
            
            with col2:
                if st.button("💰 Calcular Orçamento"):
                    st.info("Funcionalidade de orçamento será implementada em breve!")
            
            with col3:
                if st.button("📄 Gerar Relatório"):
                    st.info("Funcionalidade de relatório será implementada em breve!")
        
        else:
            st.info("Nenhum componente encontrado. Adicione componentes ou importe um arquivo SketchUp.")
            
            # Formulário para adicionar componente
            with st.expander("➕ Adicionar Componente"):
                with st.form("add_component"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        comp_name = st.text_input("Nome do Componente")
                        comp_length = st.number_input("Comprimento (mm)", min_value=1.0, value=500.0)
                        comp_width = st.number_input("Largura (mm)", min_value=1.0, value=300.0)
                    
                    with col2:
                        comp_thickness = st.number_input("Espessura (mm)", min_value=1.0, value=15.0)
                        comp_quantity = st.number_input("Quantidade", min_value=1, value=1)
                        
                        material_options = {m.id: f"{m.name} ({m.thickness}mm)" for m in st.session_state.materials}
                        comp_material_id = st.selectbox("Material", options=list(material_options.keys()), format_func=lambda x: material_options[x])
                    
                    if st.form_submit_button("Adicionar Componente"):
                        if comp_name:
                            new_component = {
                                'name': comp_name,
                                'length': comp_length,
                                'width': comp_width,
                                'thickness': comp_thickness,
                                'quantity': comp_quantity,
                                'material_id': comp_material_id
                            }
                            
                            current_project.add_component(new_component)
                            save_project(current_project)
                            st.success(f"✅ Componente '{comp_name}' adicionado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Nome do componente é obrigatório!")

def render_cutting_diagrams():
    """Renderizar diagramas de corte"""
    st.header("📐 Diagramas de Corte")
    
    current_project = get_current_project()
    
    if not current_project:
        st.warning("Selecione um projeto primeiro.")
        return
    
    if current_project.id in st.session_state.cutting_diagrams:
        result = st.session_state.cutting_diagrams[current_project.id]
        
        # Resumo da otimização
        st.subheader("📊 Resumo da Otimização")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Chapas Necessárias", result['summary']['total_sheets'])
        
        with col2:
            st.metric("Aproveitamento", f"{result['summary']['overall_utilization']:.1f}%")
        
        with col3:
            st.metric("Desperdício", f"{result['summary']['overall_waste']:.1f}%")
        
        with col4:
            st.metric("Área Total", f"{result['summary']['total_area_sheets']:.2f} m²")
        
        st.markdown("---")
        
        # Diagramas individuais
        for i, diagram in enumerate(result['cutting_diagrams']):
            st.subheader(f"📋 Chapa {diagram['id']}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Visualização do diagrama
                fig = create_cutting_diagram_visualization(diagram)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Informações da Chapa:**")
                st.write(f"• Dimensões: {diagram['sheet_width']} x {diagram['sheet_height']} mm")
                st.write(f"• Aproveitamento: {diagram['utilization']:.1f}%")
                st.write(f"• Desperdício: {diagram['waste']:.1f}%")
                st.write(f"• Peças: {len(diagram['pieces'])}")
                
                st.write("**Lista de Peças:**")
                for piece in diagram['pieces']:
                    st.write(f"• {piece['name']}")
                    st.caption(f"  {piece['width']:.0f} x {piece['height']:.0f} mm")
    
    else:
        st.info("Nenhum diagrama de corte gerado. Vá para 'Projetos' e clique em 'Gerar Plano de Corte'.")

def render_sketchup_import():
    """Renderizar importação de SketchUp"""
    st.header("📤 Importar SketchUp")
    
    st.markdown("""
    ### Como usar:
    1. Faça upload do seu arquivo SketchUp (.skp)
    2. O sistema extrairá automaticamente os componentes
    3. Revise e ajuste os componentes se necessário
    4. Crie um novo projeto ou adicione ao projeto atual
    """)
    
    # Demo de upload
    parse_result = demo_sketchup_upload()
    
    if parse_result and parse_result.success:
        st.markdown("---")
        
        # Opções de importação
        st.subheader("🎯 Opções de Importação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Nome do Projeto:",
                value=parse_result.model_info.get('filename', 'Projeto SketchUp').replace('.skp', '')
            )
        
        with col2:
            import_option = st.radio(
                "Importar como:",
                ["Novo Projeto", "Adicionar ao Projeto Atual"]
            )
        
        if st.button("🚀 Importar Projeto", type="primary"):
            try:
                # Criar projeto a partir do resultado do parser
                project_data = create_project_from_sketchup(parse_result, project_name)
                
                if import_option == "Novo Projeto":
                    # Criar novo projeto
                    new_id = max([p.id for p in st.session_state.projects]) + 1 if st.session_state.projects else 1
                    
                    new_project = Project(
                        id=new_id,
                        name=project_data['name'],
                        description=project_data['description']
                    )
                    
                    # Adicionar componentes
                    for comp in project_data['components']:
                        new_project.add_component(comp)
                    
                    st.session_state.projects.append(new_project)
                    st.session_state.current_project_id = new_id
                    
                    st.success(f"✅ Projeto '{project_name}' criado com sucesso!")
                    st.success(f"📊 {len(project_data['components'])} componentes importados")
                
                else:
                    # Adicionar ao projeto atual
                    current_project = get_current_project()
                    if current_project:
                        for comp in project_data['components']:
                            current_project.add_component(comp)
                        
                        save_project(current_project)
                        
                        st.success(f"✅ {len(project_data['components'])} componentes adicionados ao projeto atual!")
                    else:
                        st.error("Nenhum projeto atual selecionado!")
                
                # Mostrar warnings se houver
                if parse_result.warnings:
                    st.warning("⚠️ Avisos durante a importação:")
                    for warning in parse_result.warnings:
                        st.warning(f"• {warning}")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erro ao importar projeto: {str(e)}")

def render_materials():
    """Renderizar gerenciador de materiais"""
    st.header("📦 Materiais")
    
    # Lista de materiais
    st.subheader("📋 Materiais Disponíveis")
    
    materials_data = []
    for material in st.session_state.materials:
        materials_data.append({
            'Nome': material.name,
            'Espessura (mm)': material.thickness,
            'Preço': material.get_price_display(),
            'Categoria': material.category,
            'Densidade (kg/m³)': material.density,
            'Ativo': "✅" if material.is_active else "❌"
        })
    
    df = pd.DataFrame(materials_data)
    st.dataframe(df, use_container_width=True)
    
    # Adicionar novo material
    with st.expander("➕ Adicionar Material"):
        with st.form("add_material"):
            col1, col2 = st.columns(2)
            
            with col1:
                mat_name = st.text_input("Nome do Material")
                mat_thickness = st.number_input("Espessura (mm)", min_value=1.0, value=15.0)
                mat_price = st.number_input("Preço por m²", min_value=0.01, value=50.00)
                mat_density = st.number_input("Densidade (kg/m³)", min_value=100.0, value=750.0)
            
            with col2:
                mat_category = st.selectbox("Categoria", ["Madeira", "Madeira Reconstituída", "Madeira Laminada", "Metal", "Plástico"])
                mat_supplier = st.text_input("Fornecedor")
                mat_color = st.color_picker("Cor", "#8B4513")
                mat_description = st.text_area("Descrição")
            
            if st.form_submit_button("Adicionar Material"):
                if mat_name:
                    new_id = max([m.id for m in st.session_state.materials]) + 1
                    
                    new_material = Material(
                        id=new_id,
                        name=mat_name,
                        thickness=mat_thickness,
                        price_per_unit=mat_price,
                        density=mat_density,
                        category=mat_category,
                        supplier=mat_supplier,
                        color=mat_color,
                        description=mat_description
                    )
                    
                    st.session_state.materials.append(new_material)
                    st.success(f"✅ Material '{mat_name}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Nome do material é obrigatório!")

def render_reports():
    """Renderizar relatórios"""
    st.header("📊 Relatórios")
    
    current_project = get_current_project()
    
    if not current_project:
        st.warning("Selecione um projeto primeiro.")
        return
    
    # Relatório de componentes
    st.subheader("📋 Relatório de Componentes")
    
    if current_project.components:
        # Gráfico de distribuição por material
        material_distribution = {}
        for comp in current_project.components:
            material_id = comp.get('material_id', 1)
            material = get_material_by_id(st.session_state.materials, material_id)
            material_name = material.name if material else "Desconhecido"
            
            if material_name not in material_distribution:
                material_distribution[material_name] = 0
            
            area = (comp['length'] * comp['width'] * comp['quantity']) / 1000000
            material_distribution[material_name] += area
        
        # Gráfico de pizza
        fig_pie = px.pie(
            values=list(material_distribution.values()),
            names=list(material_distribution.keys()),
            title="Distribuição de Área por Material (m²)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Gráfico de barras - componentes por quantidade
        component_quantities = [(comp['name'], comp['quantity']) for comp in current_project.components]
        component_quantities.sort(key=lambda x: x[1], reverse=True)
        
        if component_quantities:
            fig_bar = px.bar(
                x=[item[1] for item in component_quantities],
                y=[item[0] for item in component_quantities],
                orientation='h',
                title="Quantidade por Componente",
                labels={'x': 'Quantidade', 'y': 'Componente'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Estatísticas resumidas
        st.subheader("📈 Estatísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_components = sum(comp['quantity'] for comp in current_project.components)
        total_area = current_project.calculate_total_area()
        total_volume = current_project.calculate_total_volume()
        unique_materials = len(set(comp.get('material_id', 1) for comp in current_project.components))
        
        with col1:
            st.metric("Total de Peças", total_components)
        
        with col2:
            st.metric("Área Total", f"{total_area:.2f} m²")
        
        with col3:
            st.metric("Volume Total", f"{total_volume:.3f} m³")
        
        with col4:
            st.metric("Materiais Únicos", unique_materials)
    
    else:
        st.info("Nenhum componente encontrado no projeto atual.")

def main():
    """Função principal da aplicação"""
    # Inicializar estado da sessão
    init_session_state()
    
    # Sidebar para navegação
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/2e7bb8/white?text=CutList+Pro", width=200)
        
        st.markdown("---")
        
        page = st.radio(
            "🧭 Navegação",
            [
                "🏠 Dashboard",
                "📁 Projetos", 
                "📐 Diagramas de Corte",
                "📤 Importar SketchUp",
                "📦 Materiais",
                "📊 Relatórios"
            ]
        )
        
        st.markdown("---")
        
        # Informações do projeto atual
        current_project = get_current_project()
        if current_project:
            st.write("**Projeto Atual:**")
            st.write(f"📋 {current_project.name}")
            st.write(f"🔧 {len(current_project.components)} componentes")
            st.write(f"📏 {current_project.calculate_total_area():.2f} m²")
        
        st.markdown("---")
        
        # Links úteis
        st.write("**Links Úteis:**")
        st.markdown("• [GitHub](https://github.com)")
        st.markdown("• [Documentação](https://docs.cutlistpro.com)")
        st.markdown("• [Suporte](mailto:suporte@cutlistpro.com)")
    
    # Renderizar página selecionada
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "📁 Projetos":
        render_project_manager()
    elif page == "📐 Diagramas de Corte":
        render_cutting_diagrams()
    elif page == "📤 Importar SketchUp":
        render_sketchup_import()
    elif page == "📦 Materiais":
        render_materials()
    elif page == "📊 Relatórios":
        render_reports()

if __name__ == "__main__":
    main()

