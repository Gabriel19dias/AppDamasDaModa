# Controle de Vendas, Cadastro e Estoque

Este projeto tem como objetivo desenvolver um sistema completo de **controle de vendas**, **cadastro de produtos** e **acompanhamento de estoque**. O sistema utiliza o **Firebase Realtime Database** para o armazenamento de dados e a biblioteca **Streamlit** para criar uma interface interativa e moderna.

## Funcionalidades

- **Cadastro de Produtos**: Permite cadastrar novos produtos com informações como nome, descrição, preço e quantidade em estoque.
- **Controle de Vendas**: Realiza o registro de vendas, atualizando o estoque automaticamente.
- **Acompanhamento de Estoque**: Exibe em tempo real o estado do estoque, permitindo o controle sobre a quantidade de produtos disponíveis.
- **Exportação para Excel**: Permite exportar os dados do estoque e vendas para um arquivo Excel, facilitando o acompanhamento e análise.
- **Integração com Firebase**: Todos os dados são armazenados no **Firebase Realtime Database**, garantindo sincronização em tempo real entre a interface e o banco de dados.

## Tecnologias Utilizadas

- **Streamlit**: Biblioteca Python para criar interfaces web interativas.
- **Firebase**: Banco de dados em tempo real para armazenar dados de vendas, produtos e estoque.
- **Pandas**: Biblioteca Python para manipulação de dados e exportação para Excel.
- **openpyxl**: Biblioteca utilizada para manipulação de arquivos Excel.

## Como Rodar o Projeto

### 1. Instalar as Dependências

Clone o repositório e instale as dependências necessárias:

```bash
git clone https://github.com/seu-usuario/controle-vendas-estoque.git
cd controle-vendas-estoque
pip install -r requirements.txt
