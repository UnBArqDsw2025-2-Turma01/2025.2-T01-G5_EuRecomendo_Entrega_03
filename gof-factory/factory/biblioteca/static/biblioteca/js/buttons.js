
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