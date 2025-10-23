class ButtonBase {
  constructor(data) {
    this.data = data;
    this.button = document.createElement('button');
    this.button.innerText = data.label || 'Botão';
  }
  render() {
    return this.button;
  }
}

class LikeButton extends ButtonBase {
  render() {
    const btn = super.render(); 
    btn.classList.add('like-button'); 
    btn.addEventListener('click', () => {
      alert(`Você curtiu o item ${this.data.target_id}`);
    });
    return btn;
  }
}

class ShareButton extends ButtonBase {
  render() {
    const btn = super.render();
    btn.classList.add('share-button');

    btn.addEventListener('click', () => {
      const shareUrl = window.location.origin + this.data.url;
      prompt('Copie o link para compartilhar:', shareUrl);
    });
    return btn;
  }
}

function buttonFactory(data) {
  switch (data.type) {
    case 'like':
      return new LikeButton(data);
    case 'share':
      return new ShareButton(data);
    default:
      return new ButtonBase(data);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('button-container');

  fetch('/biblioteca/api/buttons/')
    .then(res => res.json()) 
    .then(buttons => {
      
      buttons.forEach(data => {
        const btnObject = buttonFactory(data);
        const btnElement = btnObject.render();
        container.appendChild(btnElement);
      });
    })
    .catch(error => {
        console.error("Erro ao buscar botões:", error);
        container.innerText = "Não foi possível carregar os botões.";
    });
});