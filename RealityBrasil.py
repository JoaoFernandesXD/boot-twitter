from bs4 import BeautifulSoup
import requests
import pandas as pd
import tweepy
URL = 'https://gshow.globo.com/realities/bbb/bbb-23/'
from playwright.sync_api import sync_playwright
import time
import os
current_path = os.path.dirname(os.path.realpath(__file__))

def site(url):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
        }
    req = requests.get(url, headers=header)
    soup = BeautifulSoup(req.text, 'html.parser')
    card = soup.find_all("div", {"class":"feed-post-body"})
    lista_card = []
    for corpo in card:
        titulo = corpo.find('h2')
        if titulo:
            titulo = titulo.getText()
        descricao = corpo.find("div", {"class":"feed-post-body-resumo"})
        if descricao:
            descricao = descricao.getText()
        pass
        imagem = corpo.find("img", {"class":"bstn-fd-picture-image"})
        if imagem:
            imagem = imagem.get('src')
            lista_card.append({
                'titulo': titulo,
                'descricao': descricao,
                'imagem': imagem
            })
    return lista_card

def save_img(url):
    filename = url.split('/')[-1]
    filepath = 'files/' + filename
    r = requests.get(url, allow_redirects=True)
    open(filepath, 'wb').write(r.content)

def save_csv():
    lista_card = site(URL)
    df = pd.DataFrame(lista_card)
    df.to_csv('post.csv', sep=';', index=False)

def postar_twitter(mensagem):
    # Insira suas chaves de autenticação aqui, caso for usar direto pela API
    client = tweepy.Client(
        consumer_key="CONSUMER KEY",
        consumer_secret="CONSUMER SECRET",
        access_token="ACCESS TOKEN",
        access_token_secret="ACCESS TOKEN SECRET")
    response =  client.create_tweet(text=mensagem) 
    print(response)

def verificar():
    if not os.path.exists('post.csv'):
        save_csv()
        return
    df = pd.read_csv('post.csv', delimiter=';')
    lista_card = site(URL)
    visto = df['titulo'].values.tolist()
    for item in lista_card:
        if item['titulo'] not in visto:
            print(item['titulo'])
            df = pd.concat([df, pd.DataFrame([item])], ignore_index=True)
            save_img(item["imagem"])
            imagem = item["imagem"].split('/')[-1]
            if item["titulo"] is not None and item["descricao"] is not None :
                mensagem = item["titulo"] + " " + item["descricao"] + " " + "#BBB23 #RealitysBR "
            #postar_twitter(item["titulo"] + " " + item["descricao"] + " " + "#BBB23 #CasaDeVidro")
            executar(imagem, mensagem)
            os.remove('files/' + imagem)
    df.to_csv('post.csv', sep=';', index=False)

def page_login(usuario, senha, page, URL):
    page.goto(URL)
    page.fill('input[name="text"]', usuario)
    page.locator('div[role="button"]',has_text='Avançar').click()
    page.fill('input[name="password"]', senha)
    page.locator('div[role="button"]',has_text='Entrar').click()

    time.sleep(5)

def post_tweet(page, mensagem, path):
    page.fill('div[data-testid="tweetTextarea_0"]',mensagem)
    post_media(page, path)
    page.mouse.click(1323, 760);
    page.mouse.click(1323, 760);
    print('cliquei')
    page.get_by_test_id("tweetButtonInline").click()
    time.sleep(3)

def post_media(page, path):
    time.sleep(6)
    page.get_by_test_id('fileInput').set_input_files(path)
    time.sleep(6)

def executar(imagem, texto):
    ## Configuração de usuario
    usuario = 'Nome aqui'
    senha = 'SENHA AQUI'
    mensagem = texto
    URL = 'https://twitter.com/i/flow/login'
    path = f'{current_path}/files/{imagem}'
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--start-maximized'], headless=False)
        page = browser.new_page(no_viewport=True)
        page_login(usuario, senha, page, URL)
        post_tweet(page, mensagem, path)

def main():
    verificar()
    

if __name__ == "__main__":
    while True:
        main()
        time.sleep(600)
        print('Verificou')