Orca Tracker

Sistema de Previsão Automática GIS para Navegação Segura

O Orca Tracker Pro é um radar algorítmico desenvolvido do zero para cruzar dados biológicos e oceanográficos, prevendo zonas de alto risco de interação com Orcas Ibéricas ao longo da costa. Este projeto foi criado especificamente para garantir um planeamento de rotas seguro durante a Volta a Portugal à Vela.

Funcionalidades Principais

HeatMap Dinâmico: Visualização de zonas de risco cruzando dados de temperatura, alimento e profundidade.

Dados em Tempo Real: Integração com a API OGC do Instituto Hidrográfico para mapear as últimas 40 interações reais com orcas.

Análise Espacial (Draw Tool): Ferramenta para desenhar polígonos no mapa e extrair métricas oceanográficas médias e as coordenadas exatas de perigo para o GPS do barco.

Filtros Anti-Terra: Lógica geográfica embutida para garantir que o mock de previsão não gera avistamentos fora do mar.

O Cérebro do Algoritmo

O modelo de Scoring baseia-se na procura do Atum Rabilho, a presa favorita das orcas ibéricas. O algoritmo avalia 3 variáveis cruciais:

Temperatura (SST): Correntes de água entre 15ºC e 18ºC (o sweet spot do atum).

Clorofila: Zonas com mais de 3.5 mg/m³, indicando fenómenos de upwelling e forte densidade na cadeia alimentar.

Batimetria: Zonas fundas e drop-offs (profundidade inferior a -200m) utilizadas pelos predadores para encurralar presas.

Como Correr o Projeto (Localmente)

1. Instalar as dependências:

pip install -r requirements.txt


(Nota: Recomenda-se Python 3.10 ou 3.11 para máxima compatibilidade com as bibliotecas espaciais).

2. Iniciar a App:

streamlit run orca_tracker_setup.py


por Trás do Código

Zé Castro
**Zé Castro** Estudante de 18 anos, prestes a ir a universidade que propôs fazer parte na Volta a Portugal à Vela. 

Desenvolvi este radar algorítmico do zero para prever as zonas de risco, cruzar dados reais e salvar o leme do barco durante a regata.
