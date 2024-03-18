document.addEventListener("DOMContentLoaded", function () {
    // Esconde o loader assim que o conteúdo estiver carregado
    document.getElementById('container_loader').style.display = 'none';
});

document.addEventListener('DOMContentLoaded', function () {
    // Obtém todas as tags <a> na página
    let links = document.getElementsByTagName('a');
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function startLoading(){
            if (!event.currentTarget.classList.contains('nao-carregar')) {
                document.getElementById('container_loader').style.display = 'flex';
                // Define um tempo limite para a exibição da animação (por exemplo, 5 segundos)
                setTimeout(function() {
                    document.getElementById('container_loader').style.display = 'none';
                }, 5000); // Tempo limite em milissegundos (5 segundos neste exemplo)
            }
        })
    }
});