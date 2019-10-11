# -*- coding: utf-8 -*-

from flask import Flask, jsonify
import os
import re
import requests
from bs4 import BeautifulSoup

dc = {
"jobs":[]
}
class PegarEmpregos:
    def __init__(self, pag):
        url_base = "http://empregacampinas.com.br/categoria/vaga/page/{}/".format(pag)
        self.pagina = BeautifulSoup(requests.get(url_base).text, "lxml")
        self.pegar_vagas()

    def pegar_vagas(self):
        try: return [self.pegar_detalhes_vaga(vaga["href"]) for vaga in self.pagina.findAll("a") \
                if(re.search("empregacampinas.com.br/\d{4}", vaga["href"]))]
        except Exception as erro: pass#print('ERRO EM PEGAR VAGAS({})'.format(erro))


    vagas = {
    "jobs":[]
    }
    def pegar_detalhes_vaga(self, url):

        link = url
        pagina = BeautifulSoup(requests.get(url).text, "lxml")
        html = pagina.find(class_="col-lg-8 conteudo-vaga")

        detalhes = []
        try: vaga = self.extrai_vaga_cidade_quantiade(html)[0]
        except Exception as erro: return False

        detalhes.append(vaga)

        try: codigo = re.findall('\d+', re.findall("\(\n\d{7}\s+\)", html.text)[0])[0]
        except: codigo = ''

        try: data_validade = re.findall("\d{2}\/\d{2}\/\d{4}", re.findall("assunto\saté\so\sdia\s\d{2}\/\d{2}\/\d{4}", pagina.text)[0])
        except: data_validade = ""


        for contagem, topico in enumerate(html.findAll("p")):
            if(contagem in [2, 3, 4, 5, 6]):  detalhes.append(topico.text)
            elif(contagem >= 7):
                try: self.validar_email_telefone(detalhes, topico.text)
                except Exception as erro:print("SEM CONTATO", erro)
        try:
            vagas = {"vaga": detalhes[0], "salario": detalhes[3][8:], "desc_com": detalhes[4][11:]+'\n\n'+detalhes[2].split('/')[0], "validade": "".join(data_validade), "codigo": codigo,
                     "desc_brev": detalhes[4][11:50],"requisitos": detalhes[1][19:], "Beneficios": detalhes[2][12:], "contato": detalhes[6], "link": link, 'search' : vaga }
            dc["jobs"].append(vagas)

        except Exception as erro: print(erro)

    def extrai_vaga_cidade_quantiade(self, html): return str(html.h1.span)[7:-8].split('/')


    def validar_email_telefone(self, detalhes, txt):
        valida = ["^([1-9]{2}) 9[7-9]{1}[0-9]{3}-[0-9]{4}$",
                  "[a-zA-Z0-9]+[a-zA-Z0-9_.-]+@{1}[a-zA-Z0-9_.-]*\\.+[a-z]{2,4}"]
        for conta in range(2):
            try: detalhes.append(re.findall(valida[conta], txt)[0])
            except Exception as erro: pass

################# EXEMPLO DE USO

def api ():
    for i in range(15):
        PegarEmpregos(i)











#from datetime import datetime


app = Flask(__name__)


#def sec():
    #new = datetime.now()
    #sec = new.second
    #return str()




@app.route('/',methods = ['GET'])
def get_Api():

    return jsonify(dc)






@app.route('/<string:arg>',methods = ['GET'])
def get_Api_search(arg):


    search = [i for i in dc['jobs'] if i["search"] == arg ]

    return jsonify(search)







#host='0.0.0.0',





if __name__== '__main__':
    api()

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True,host='0.0.0.0',port=port)
