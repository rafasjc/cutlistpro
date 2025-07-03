# CutList Pro - Planos de Corte e Orçamentos

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cutlist-pro.streamlit.app)

Uma aplicação web avançada para geração de planos de corte e orçamentos para projetos de marcenaria, superior ao OpenCutList.

## 🚀 Funcionalidades

### ✅ Principais Recursos
- **Upload de arquivos SketchUp** (.skp) com processamento automático
- **3 algoritmos de otimização** de cortes avançados
- **Visualização gráfica** de diagramas de corte em tempo real
- **Relatórios profissionais** em múltiplos formatos (PDF, CSV, Excel)
- **Estimativas detalhadas** de custo e material
- **Interface moderna** e responsiva
- **Biblioteca de materiais** com preços brasileiros

### 🔧 Algoritmos de Otimização
1. **Bottom-Left Fill** - Otimização geral
2. **Best Fit Decreasing** - Minimização de desperdício  
3. **Guillotine Split** - Cortes automatizados

### 📊 Relatórios Disponíveis
- Lista de peças (PDF, CSV, Excel, JSON)
- Estimativa de custo detalhada
- Diagramas de corte visuais
- Análise de desperdício

## 🎯 Melhorias sobre o OpenCutList

| Recurso | OpenCutList | CutList Pro |
|---------|-------------|-------------|
| Interface | Básica | Moderna (Streamlit) |
| Algoritmos | 1 | 3 avançados |
| Relatórios | Limitados | Múltiplos formatos |
| Upload SketchUp | Plugin | Web nativo |
| Visualização | Simples | Gráfica avançada |
| Estimativas | Básicas | Detalhadas |
| Materiais | Genéricos | Mercado brasileiro |

## 🛠️ Tecnologias

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **Algoritmos**: NumPy, SciPy
- **Visualização**: Plotly, Matplotlib
- **Relatórios**: ReportLab, OpenPyXL
- **Parser SketchUp**: SketchUp API / Custom Parser

## 📦 Instalação

### Pré-requisitos
- Python 3.11+
- Git

### Instalação Local
```bash
# Clonar repositório
git clone https://github.com/usuario/cutlist-pro-streamlit.git
cd cutlist-pro-streamlit

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run src/app.py
```

### Deploy no Streamlit Community Cloud
1. Fork este repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte sua conta GitHub
4. Selecione o repositório e arquivo `src/app.py`
5. Deploy automático!

## 🚀 Uso Rápido

### 1. Upload de Arquivo SketchUp
- Acesse a aplicação
- Faça upload do arquivo .skp
- Aguarde processamento automático

### 2. Configurar Materiais
- Selecione materiais da biblioteca
- Ajuste preços se necessário
- Configure tamanhos de chapas

### 3. Gerar Plano de Corte
- Escolha algoritmo de otimização
- Configure margem de corte (kerf)
- Visualize resultado em tempo real

### 4. Exportar Relatórios
- Selecione formato desejado
- Download automático
- Compartilhe com clientes

## 📁 Estrutura do Projeto

```
cutlist-pro-streamlit/
├── src/
│   ├── app.py                 # Aplicação principal Streamlit
│   ├── algorithms/            # Algoritmos de otimização
│   │   ├── cutting_optimizer.py
│   │   ├── cost_calculator.py
│   │   └── bin_packing.py
│   ├── parsers/              # Parsers de arquivos
│   │   ├── sketchup_parser.py
│   │   └── file_processor.py
│   ├── reports/              # Geração de relatórios
│   │   ├── pdf_generator.py
│   │   ├── csv_generator.py
│   │   └── excel_generator.py
│   ├── models/               # Modelos de dados
│   │   ├── project.py
│   │   ├── component.py
│   │   └── material.py
│   └── utils/                # Utilitários
│       ├── visualizations.py
│       └── helpers.py
├── assets/                   # Recursos estáticos
│   ├── images/
│   └── examples/
├── docs/                     # Documentação
│   ├── user_guide.md
│   ├── api_reference.md
│   └── algorithms.md
├── tests/                    # Testes
│   ├── test_algorithms.py
│   ├── test_parsers.py
│   └── test_reports.py
├── requirements.txt          # Dependências Python
├── .streamlit/              # Configurações Streamlit
│   └── config.toml
└── README.md                # Este arquivo
```

## 🎨 Screenshots

### Dashboard Principal
![Dashboard](assets/images/dashboard.png)

### Upload de Arquivo
![Upload](assets/images/upload.png)

### Diagrama de Corte
![Cutting Diagram](assets/images/cutting_diagram.png)

### Relatórios
![Reports](assets/images/reports.png)

## 📊 Exemplo de Uso

### Projeto: Estante de Livros
- **Componentes**: 4 peças
- **Material**: MDF 15mm
- **Aproveitamento**: 85%
- **Desperdício**: 15%
- **Custo total**: R$ 71,27

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Roadmap

### Versão 1.1
- [ ] Parser completo de SketchUp
- [ ] Autenticação de usuários
- [ ] Salvamento de projetos
- [ ] Histórico de otimizações

### Versão 1.2
- [ ] Integração com fornecedores
- [ ] API REST completa
- [ ] App mobile
- [ ] Algoritmos de IA

### Versão 2.0
- [ ] Integração com máquinas CNC
- [ ] Marketplace de materiais
- [ ] Sistema de orçamentos
- [ ] Multi-idiomas

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Rafael Oliveira**
- Arquiteto e Desenvolvedor
- Email: contato@exemplo.com
- LinkedIn: [linkedin.com/in/rafael-oliveira](https://linkedin.com/in/rafael-oliveira)

## 🙏 Agradecimentos

- Comunidade OpenCutList pela inspiração
- Streamlit pela plataforma incrível
- Comunidade Python pela base sólida

## 📈 Status do Projeto

- ✅ **MVP Completo**: Todas funcionalidades básicas implementadas
- ✅ **Deploy Ativo**: Aplicação rodando em produção
- 🔄 **Em Desenvolvimento**: Melhorias contínuas
- 📊 **Testes**: Validação com usuários reais

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/new)

