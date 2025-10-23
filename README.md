# Implementações


## Filtro de buscas

A implementação feita foi do Decorator no back-end da aplicação.

<font size="2"><p style="text-align: center"><b>Figura 1:</b> Diagrama Decorator</div>

<div style="text-align: center;">

![Diagrama]()

</div>

<font size="2"><p style="text-align: center"><b>Autores:</b> Sophia Silva e Renan, 2025</p></font>


### Código

Foram implementados os códigos no padrão factory. Seguem abaixo:

```python


```

<font size="2"><p style="text-align: center"><b>Autor/es:</b> Sophia Silva e Renan Vieira, 2025</p></font>


### Passo a Passo para Rodar os Códigos

Antes de tudo, certifique-se e ter o python3 e django admin instalado no seu computador.

1. Acesse a branch [Decorator - Sophia e Renan](https://github.com/UnBArqDsw2025-2-Turma01/2025.2-T01-G5_EuRecomendo_Entrega_03/tree/feat-estrutural-decorator-sophia-renan) e faça download e digite no terminal
```
git checkout feat-estrutural-decorator-sophia-renan
```
2. No terminal, digite o seguinte comando para acessar a pasta 
``` 
cd gof-factory/factory 
```
3. Rode as migrações com 
```python
python3 manage.py makemigrations
python3 manage.py migrate
```
4. Crie seu super usuário
```python
python3 manage.py createsuperuser
```
5. Execute o projeto com
```python
python3 manage.py runserver
```
6. Acesse o localhost no seu navegador, adicione o /admin/ no final da url e faça login com seu usuário. Adicione 3 livros novos.
7. Apague a url do admin, acesse /biblioteca/home/ e interaja com os botões de curtir, compartilhar e salvar!

### Vídeo da execução

<font size="2"><p style="text-align: center">Vídeo - Decorator.</p></font>

<center>

</center>

<font size="2"><p style="text-align: center">Autor/a: [](), 2025.</p></font>

### Histórico de Versões

| Versão | Data       | Descrição                                                                    | Autor(es)                                                                                        | Revisor(es)                                   | Detalhes da Revisão |
| ------ | ---------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------- | ------------------- |
| 0.1    | 23/10/2025 | Criação inicial do documento                     | [Sophia Silva](https://github.com/sophiassilva) |[Renan Vieira](https://github.com/R-enanVieira) |                     |
