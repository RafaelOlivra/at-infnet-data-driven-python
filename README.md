# Dashboard - StatsBombPy

## Descrição do Projeto

Este projeto foi desenvolvido com o objetivo de fornecer uma plataforma prática para explorar dados de futebol de maneira visual e interativa. Utilizando a biblioteca **StatsBombPy**, conseguimos acessar uma vasta gama de dados detalhados sobre partidas de futebol, permitindo análises personalizadas e insights valiosos para fãs, analistas e entusiastas do esporte. O dashboard conta com uma ferramenta de chat alimentada pelo **Google Gemini** que responde perguntas sobre os jogos, tornando a experiência ainda mais dinâmica.

Este projeto foi criado como parte do Assessment da disciplina **Desenvolvimento de Data-Driven Apps com Python [24E4_3]**.

---

### Autor

**Rafael Soares de Oliveira**  
Infnet - Ciência de Dados | Dezembro 2024

---

### Fonte dos Dados

Os dados utilizados neste projeto foram disponibilizados pela biblioteca StatsBomb. Para mais informações, visite o repositório oficial: [StatsBombPy GitHub](https://github.com/statsbomb/statsbombpy).

---

### Configuração de Chaves de API

Para que todas as funcionalidades do dashboard estejam disponíveis, é necessário configurar as seguintes chaves de API no arquivo `.env` na raiz do projeto:

-   `GEMINI_API_KEY=your_gemini_api_key`
-   `SERPER_API_KEY=your_serper_api_key`

Certifique-se de substituir `your_gemini_api_key`, e `your_serper_api_key` pelos valores reais das suas chaves de API correspondentes. O arquivo `.env` deve ser estruturado conforme o exemplo abaixo:

```env
GEMINI_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
```

### Inicializar o Repositório (Com venv)

Para iniciar o repositório localmente, siga os passos abaixo:

1. Crie um ambiente virtual e ative-o:

    ```console
    python -m venv .venv && source .venv/bin/activate
    ```

2. Instale as dependências necessárias:

    ```console
    pip install -r requirements.txt
    ```

3. Inicialize o Streamlit:

    ```console
    streamlit run main.py
    ```

4. Acesse o dashboard através do navegador no endereço: [http://localhost:8501](http://localhost:8501).

---
