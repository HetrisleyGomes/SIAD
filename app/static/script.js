document.addEventListener("DOMContentLoaded", function () {
    // Esconde o loader assim que o conteúdo estiver carregado
    document.getElementById('container_loader').style.display = 'none';
});

document.addEventListener('DOMContentLoaded', function () {
    // Obtém todas as tags <a> na página
    let links = document.getElementsByTagName('a');
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function startLoading(){
            document.getElementById('container_loader').style.display = 'flex';
        })
    }
});