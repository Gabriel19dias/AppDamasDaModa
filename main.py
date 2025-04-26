import streamlit as st
import requests
import pandas as pd  # Importação do pandas para manipular e exibir tabelas
import streamlit as st
import streamlit.components.v1 as components
import io
import openpyxl

# Firebase URL (sem esquecer do .json)
FIREBASE_URL = "https://appvendas-41654-default-rtdb.firebaseio.com"
# Função para adicionar fundo colorido
def adicionar_background():
    st.markdown(
        """
        <style>
        /* Detecta o tema do navegador */
        @media (prefers-color-scheme: dark) {
            .stApp {
                background: linear-gradient(to right, #333333, #444444);  /* Escuro */
                color: white;
            }
        }
        @media (prefers-color-scheme: light) {
            .stApp {
                background: linear-gradient(to right, #FFD1DC, #FFE4E1);  /* Claro */
                color: black;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Chama a função para aplicar
# Aqui chama a função pra aplicar o fundo

# Função para salvar dados no Firebase
def salvar_firebase(categoria, dados):
    url = f"{FIREBASE_URL}/{categoria}.json"
    try:
        resposta = requests.post(url, json=dados)
        if resposta.status_code == 200:
            st.success("✅ Dados salvos com sucesso!")
        else:
            st.error(f"❌ Erro ao salvar! Código {resposta.status_code}: {resposta.text}")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

# Sidebar para navegação


st.sidebar.title("Menu")
opcao = st.sidebar.radio("Escolha uma opção:", ["Cadastrar Cliente", "Cadastrar Roupa", "Registrar Venda", "Ver Tabela","Dashboard"])


# Cadastrar Cliente
if opcao == "Cadastrar Cliente":
    
    st.title("Cadastro de Cliente")
    nome = st.text_input("Nome do Cliente")
    email = st.text_input("Email do Cliente")
    telefone = st.text_input("Telefone")
    bairro = st.text_input("bairro")
    cpf = st.text_input("cpf")

    if st.button("Salvar Cliente"):
        if nome and email and telefone:
            dados_cliente = {
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "bairro":bairro,
                "cpf":cpf
            }
            salvar_firebase("clientes", dados_cliente)
        else:
            st.warning("⚠️ Preencha todos os campos!")



# Cadastrar Roupa
elif opcao == "Cadastrar Roupa":
    st.title("Cadastro de Roupa")
    nome_roupa = st.text_input("Nome da Roupa")
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")
    quantidade = st.number_input("Quantidade", min_value=1)
    tamanho = st.selectbox("Tamanho", ["PP", "P", "M", "G", "GG"])

    if st.button("Salvar Roupa"):   
        if nome_roupa and preco:
            valor_total = preco * quantidade  # Calcula o valor total da roupa

            dados_roupa = {
                "nome": nome_roupa,
                "preco": preco,
                "tamanho": tamanho,
                "quantidade": quantidade,
                "valor_total": valor_total  # Novo campo adicionado
            }
            salvar_firebase("roupas", dados_roupa)
        else:
            st.warning("⚠️ Preencha todos os campos!")

# Registrar Venas



elif opcao == "Registrar Venda":
    st.title("🛒 Registrar Venda")

    # Função para buscar clientes
    def buscar_clientes():
        url = f"{FIREBASE_URL}/clientes.json"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados:
                    return dados
            else:
                st.error(f"Erro ao buscar clientes! Código {resposta.status_code}: {resposta.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
        return {}

    # Função para buscar roupas no estoque
    def buscar_estoque():
        url = f"{FIREBASE_URL}/roupas.json"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados:
                    return dados
            else:
                st.error(f"Erro ao buscar estoque! Código {resposta.status_code}: {resposta.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
        return {}

    # Função para atualizar o estoque no Firebase
    def atualizar_estoque(chave_roupa, nova_quantidade):
        url = f"{FIREBASE_URL}/roupas/{chave_roupa}.json"
        try:
            resposta = requests.patch(url, json={"quantidade": nova_quantidade})
            if resposta.status_code == 200:
                st.success("✅ Estoque atualizado com sucesso!")
            else:
                st.error(f"Erro ao atualizar estoque! Código {resposta.status_code}: {resposta.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

    # Buscar clientes e roupas
    clientes = buscar_clientes()
    roupas = buscar_estoque()

    # Selecionar cliente e produto
    if clientes and roupas:
        lista_clientes = [dados["nome"] for chave, dados in clientes.items()]
        lista_roupas = [f"{dados['nome']} (Qtd: {dados.get('quantidade', 0)})" for chave, dados in roupas.items()]
        
        nome_cliente = st.selectbox("Selecione o Cliente", lista_clientes)
        produto_selecionado = st.selectbox("Selecione o Produto", lista_roupas)
        quantidade_vendida = st.number_input("Quantidade Vendida", min_value=1, step=1)
        desconto_percentual = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0)

        # Procurar o produto escolhido para calcular valor
        preco_unitario = 0.0
        estoque_atual = 0
        chave_produto_selecionado = None
        nome_produto_real = ""

        for chave_roupa, dados_roupa in roupas.items():
            nome_roupa_completo = f"{dados_roupa['nome']} (Qtd: {dados_roupa.get('quantidade', 0)})"
            if nome_roupa_completo == produto_selecionado:
                preco_unitario = dados_roupa.get('preco', 0.0)
                estoque_atual = dados_roupa.get('quantidade', 0)
                chave_produto_selecionado = chave_roupa
                nome_produto_real = dados_roupa['nome']
                break

        # Calcular valor total
        valor_total_sem_desconto = preco_unitario * quantidade_vendida
        valor_desconto = (desconto_percentual / 100) * valor_total_sem_desconto
        valor_total_com_desconto = valor_total_sem_desconto - valor_desconto

        st.write(f"💰 **Valor total sem desconto:** R$ {valor_total_sem_desconto:.2f}")
        st.write(f"🏷️ **Valor do desconto:** R$ {valor_desconto:.2f}")
        st.write(f"✅ **Valor final a pagar:** R$ {valor_total_com_desconto:.2f}")

        if st.button("Salvar Venda"):
            if estoque_atual >= quantidade_vendida:
                novo_estoque = estoque_atual - quantidade_vendida

                # Salvar venda
                dados_venda = {
                    "cliente": nome_cliente,
                    "produto": nome_produto_real,
                    "quantidade": quantidade_vendida,
                    "valor_unitario": preco_unitario,
                    "desconto_percentual": desconto_percentual,
                    "valor_total": valor_total_com_desconto
                }
                salvar_firebase("vendas", dados_venda)

                # Atualizar estoque
                atualizar_estoque(chave_produto_selecionado, novo_estoque)
            else:
                st.error("❌ Estoque insuficiente para essa venda!")
    else:
        st.warning("⚠️ Não há clientes ou produtos cadastrados!")

elif opcao == "Dashboard":
    st.title("📊 Dashboard de Vendas e Estoque")

    # Função para buscar dados de uma categoria
    def buscar_categoria(categoria):
        url = f"{FIREBASE_URL}/{categoria}.json"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados:
                    return dados
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
        return {}

    # Buscar dados
    clientes = buscar_categoria("clientes")
    roupas = buscar_categoria("roupas")
    vendas = buscar_categoria("vendas")

    # Filtros para produtos e clientes
    produto_filtrado = st.selectbox("Filtrar por Produto", options=["Todos"] + [roupa["nome"] for roupa in roupas.values()])
    cliente_filtrado = st.selectbox("Filtrar por Cliente", options=["Todos"] + [cliente["nome"] for cliente in clientes.values()])

    # Filtrando dados de vendas conforme o filtro
    if produto_filtrado != "Todos":
        vendas = {key: venda for key, venda in vendas.items() if venda["produto"] == produto_filtrado}
    if cliente_filtrado != "Todos":
        vendas = {key: venda for key, venda in vendas.items() if venda["cliente"] == cliente_filtrado}

    # Tratamento de dados
    total_clientes = len(clientes) if clientes else 0
    total_produtos = sum(roupa.get("quantidade", 0) for roupa in roupas.values()) if roupas else 0
    total_vendas = len(vendas) if vendas else 0
    faturamento_total = sum(venda.get("valor_total", 0.0) for venda in vendas.values()) if vendas else 0.0

    # Calcular o custo total de todas as roupas
    custo_total = sum(roupa.get("custo_total", 0.0) for roupa in roupas.values()) if roupas else 0.0

    # KPIs com fonte menor
    st.markdown("## 📈 Indicadores Principais")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Definir um estilo para a fonte menor
    kpi_style = """
        <style>
            .metric-title {
                font-size: 14px !important;
                font-weight: bold;
            }
            .metric-value {
                font-size: 16px !important;
                color: #ff4d4d;
            }
        </style>
    """
    
    st.markdown(kpi_style, unsafe_allow_html=True)
    
    col1.markdown(f'<div class="metric-title">👥 Clientes</div><div class="metric-value">{total_clientes}</div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-title">🛒 Itens no Estoque</div><div class="metric-value">{total_produtos}</div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-title">🛍️ Vendas Realizadas</div><div class="metric-value">{total_vendas}</div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-title">💰 Faturamento</div><div class="metric-value">R$ {faturamento_total:,.2f}</div>', unsafe_allow_html=True)
    col5.markdown(f'<div class="metric-title">💸 Custo Total Estoque</div><div class="metric-value">R$ {custo_total:,.2f}</div>', unsafe_allow_html=True)

    # Gráfico de vendas por produto (com filtro)
    if vendas:
        import pandas as pd
        import plotly.express as px

        vendas_df = pd.DataFrame(vendas).T  # Transforma o dict em DataFrame

        # Gráfico de faturamento por produto
        vendas_produto = vendas_df.groupby("produto")["valor_total"].sum().reset_index()

        st.markdown("## 🛒 Faturamento por Produto")
        fig = px.bar(vendas_produto, x="produto", y="valor_total", text_auto=True, labels={"valor_total": "Valor Vendido (R$)", "produto": "Produto"})
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico de vendas por cliente (com filtro)
    if vendas:
        vendas_cliente = vendas_df.groupby("cliente")["valor_total"].sum().reset_index()

        st.markdown("## Faturamento por Cliente")
        fig2 = px.pie(vendas_cliente, names="cliente", values="valor_total", title="Participação no Faturamento")
        st.plotly_chart(fig2, use_container_width=True)

    st.caption("📊 Dashboard atualizado em tempo real com dados do Firebase")

elif opcao == "Ver Tabela":
    # Função para buscar dados do Firebase e exibi-los em uma tabela
    def buscar_firebase(categoria):
        url = f"{FIREBASE_URL}/{categoria}.json"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados:
                    df = pd.DataFrame.from_dict(dados, orient='index')
                    df['firebase_id'] = df.index  # Coloca a chave como uma coluna
                    return df
                else:
                    st.info(f"Nenhum registro encontrado em {categoria}.")
            else:
                st.error(f"Erro ao buscar dados! Código {resposta.status_code}: {resposta.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio se houver erro

    # Função para apagar registro do Firebase
    def apagar_firebase(categoria, firebase_id):
        url = f"{FIREBASE_URL}/{categoria}/{firebase_id}.json"
        try:
            resposta = requests.delete(url)
            if resposta.status_code == 200:
                st.success("🗑️ Registro apagado com sucesso!")
            else:
                st.error(f"Erro ao apagar registro! Código {resposta.status_code}: {resposta.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

    st.title("🔎 Exibir e Gerenciar Registros do Firebase")
    categoria = st.selectbox("Escolha a categoria para exibir", ["clientes", "roupas", "vendas"])

    dados_df = buscar_firebase(categoria)

    if not dados_df.empty:
        # Adicionando o índice visível na tabela
        dados_df_reset = dados_df.reset_index()  # Resetando o índice para torná-lo uma coluna visível
        dados_df_reset = dados_df_reset.rename(columns={'index': 'Índice'})  # Renomeando a coluna de índice

        # Exibindo a tabela com o índice visível
        st.dataframe(dados_df_reset.sort_index(axis=1))  # Exibe ordenando as colunas

        linha_selecionada = st.number_input("Digite o número da linha que deseja apagar", min_value=0, max_value=len(dados_df)-1, step=1)

        if st.button("🗑️ Apagar Linha Selecionada"):
            try:
                firebase_id = dados_df.iloc[linha_selecionada]['firebase_id']
                apagar_firebase(categoria, firebase_id)
                st.experimental_rerun()  # Atualiza a página para refletir a exclusão
            except Exception as e:
                st.error(f"Erro ao tentar apagar: {e}")

        # Botão para exportar para Excel
        st.markdown("---")
        if st.button("📥 Exportar Tabela para Excel"):
    # Removendo a coluna 'firebase_id'
            excel_data = dados_df.drop(columns=['firebase_id'])

            # Criando um buffer em memória para armazenar o arquivo Excel
            buffer = io.BytesIO()

            # Exportando os dados para o buffer usando openpyxl como engine
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                excel_data.to_excel(writer, index=False, sheet_name="Dados Exportados")
            
            # Rewind do buffer para leitura após a escrita
            buffer.seek(0)

            # Nome do arquivo de exportação, por exemplo, com base na categoria
            categoria = 'Categoria_Exemplo'  # Ajuste isso conforme necessário

            # Exibindo o botão de download
            st.download_button(
                label="Clique para baixar",
                data=buffer,
                file_name=f"{categoria}_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info(f"Nenhum dado encontrado em {categoria}.")
