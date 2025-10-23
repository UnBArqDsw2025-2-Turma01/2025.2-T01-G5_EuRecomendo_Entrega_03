# Implementações


## 1 - ButtonHandler

A primeira implementação feita foi do Factory Method no front-end da aplicação, com o ButtonHandler para delegar a subclasses a lógica de "curtir", "compartilhar" ou "salvar na biblioteca". 

<font size="2"><p style="text-align: center"><b>Figura 1:</b> Diagrama ButtonHandler</div>

<div style="text-align: center;">

![Diagrama](/docs/assets/buttonHandlerDiagrama.png)

</div>

<font size="2"><p style="text-align: center"><b>Autores:</b> Renan Vieira e Sophia Silva, 2025</p></font>


### Código

Foram implementados os códigos no padrão factory. Seguem abaixo:

```javascript

class ButtonHandlerBase {
  constructor(element) {
    this.element = element; 
    this.data = element.dataset; 
  }

  attachEvents() {
    this.element.addEventListener('click', () => {
      this.onClick();
    });
  }
  onClick() {
    console.warn(`Ação não definida para o botão: ${this.data.action}`);
  }
}

class LikeButtonHandler extends ButtonHandlerBase {
  onClick() {
    this.element.classList.toggle('liked');
    const svg = this.element.querySelector('svg');
    svg.style.fill = 'none';
    const isLiked = this.element.classList.contains('liked');
    if (isLiked) {
      alert(`Você CURTIU o livro ID: ${this.data.bookId}`);
    } else {
      alert(`Você DESCURTIU o livro ID: ${this.data.bookId}`);
    }
  }
}

class ShareButtonHandler extends ButtonHandlerBase {
  onClick() {
    const title = this.data.bookTitle;
    const author = this.data.bookAuthor;
    const url = window.location.href;
    const shareText = `Confira este livro incrível: "${title}" de ${author}. Veja mais em: ${url}`;
    if (navigator.share) {
      navigator.share({
        title: `Biblioteca: ${title}`,
        text: shareText,
        url: url,
      }).catch(err => console.error("Erro ao compartilhar:", err));
    } else {
      prompt('Copie o link para compartilhar:', shareText);
    }
  }
}

class SaveButtonHandler extends ButtonHandlerBase {
    onClick() {
      this.element.classList.toggle('saved');
      const svg = this.element.querySelector('svg');
      svg.style.fill = 'none';
      const isSaved = this.element.classList.contains('saved');
      if (isSaved) {
        alert(`Você SALVOU o livro ID: ${this.data.bookId}`);
      } else {
        alert(`Você REMOVEU o livro ID: ${this.data.bookId}`);
      }
    }
}

function buttonFactory(element) {
  const action = element.dataset.action;

  switch (action) {
    case 'like':
      return new LikeButtonHandler(element);
    case 'share':
      return new ShareButtonHandler(element);
    case 'save':
      return new SaveButtonHandler(element);
    default:
      return new ButtonHandlerBase(element);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const allButtons = document.querySelectorAll('.action-btn');
  allButtons.forEach(buttonElement => {
    const handler = buttonFactory(buttonElement);
    handler.attachEvents();
  });
});
```

<font size="2"><p style="text-align: center"><b>Autor/es:</b> Sophia Silva e Renan Vieira, 2025</p></font>


### Passo a Passo para Rodar os Códigos

Antes de tudo, certifique-se e ter o python3 e django admin instalado no seu computador.

1. Acesse a branch [Factory - ButtonHandler - Sophia e Renan](https://github.com/UnBArqDsw2025-2-Turma01/2025.2-T01-G5_EuRecomendo_Entrega_03/tree/feat-criacional-factory-sophia-renan) e faça download ou digite no terminal
```
git checkout feat-criacional-factory-sophia-renan
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

<font size="2"><p style="text-align: center">Vídeo 1 - Factory Method.</p></font>

<center>
<iframe width="560" height="315" src="https://www.youtube.com/embed/yFtV18MTrfU?si=x5kWtZztstdT5e83" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</center>

<font size="2"><p style="text-align: center">Autora: [Sophia Silva](https://github.com/sophiassilva), 2025.</p></font>

### Histórico de Versões

| Versão | Data       | Descrição                                                                    | Autor(es)                                                                                        | Revisor(es)                                   | Detalhes da Revisão |
| ------ | ---------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------- | ------------------- |
| 0.1    | 22/10/2025 | Criação inicial e adição do que foi implementado                     | [Renan Vieira](https://github.com/R-enanVieira) | [Sophia Silva](https://github.com/sophiassilva) |                     |
