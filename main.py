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
        except: pass


    vagas = {
    "jobs":[]
    }
    def pegar_detalhes_vaga(self, url):

        link = url
        pagina = BeautifulSoup(requests.get(url).text, "lxml")
        html = pagina.find(class_="col-lg-8 conteudo-vaga")

        detalhes = []
        try: detalhes.append(self.limpar(html.h1.span)[17:-16])
        except: return False

        try: codigo = re.findall("\d+", "".join(re.findall("\n\s+\d+\s+\){1}", pagina.text)))[0]
        except: pass

        try: data_validade = re.findall("\d{2}\/\d{2}\/\d{4}", re.findall("assunto\saté\so\sdia\s\d{2}\/\d{2}\/\d{4}", pagina.text)[0])
        except: data_validade = ""


        for contagem, topico in enumerate(html.findAll("p")):
            if(contagem == 2 or contagem == 3 or contagem == 4 or contagem == 5
               or contagem == 6):
                    detalhes.append(topico.text)
            elif(contagem >= 7):
                try: self.validar_email_telefone(detalhes, topico.text)
                except Exception as erro:print("SEM CONTATO", erro)

        vagas = {"vaga": detalhes[0].split('/')[0].split(' ')[0]+ ' ' + detalhes[0].split('/')[0].split(' ')[1]+ ' ' + detalhes[0].split('/')[0].split(' ')[2], "salario": detalhes[3][8:], "desc_com": detalhes[4][11:]+'\n\n'+detalhes[2].split('/')[0], "validade": "".join(data_validade),
                 "desc_brev": detalhes[4][11:50]+detalhes[0].split('/')[1],"requisitos": detalhes[1][19:], "Beneficios": detalhes[2][12:], "contato": detalhes[6], "link": link}

        dc["jobs"].append(vagas)

    def limpar(self, txt): return str(txt).replace("\n", "").replace("\t", "").replace("\b", "")


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


    search = [i for i in dc['jobs'] if i["vaga"] == arg ]

    return jsonify(search)







#host='0.0.0.0',





if __name__== '__main__':
    api()

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True,host='0.0.0.0',port=port)
