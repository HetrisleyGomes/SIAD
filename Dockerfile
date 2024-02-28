# Use a imagem oficial do Ubuntu como base
FROM python:3.11.4-slim-buster

# Defina o diretório de trabalho como /app
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt /app/requirements.txt

# Instale as dependências do projeto
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Copie o conteúdo do diretório atual para o diretório de trabalho
COPY ./app .

# Exponha a porta 5000 (ou qualquer outra porta que sua aplicação Flask utilize)
EXPOSE 5000
