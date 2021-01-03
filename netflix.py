import codecs
import requests,json,re,random
import pandas as pd
import time
from multiprocessing import Process,Manager


decode_hex = codecs.getdecoder("hex_codec")

def substituicoes(texto):
    a = texto.find('\\x')
    while a >= 0:
        hexdigito = texto[a+2:a+4]
        texto = texto[:a] + decode_hex(hexdigito)[0].decode() + texto[a+4:]
        a = texto.find('\\x')
    return texto

def recupera_url_item(urlnetflixitem):
    #netflixitem = 'https://www.netflix.com/br/title/70102779'
    r = requests.get(urlnetflixitem)
    dados = r.text
    comeco = dados.index('netflix.reactContext')
    dado_json = 'Não encontrado'
    if comeco>0:
      comeco=comeco+len('netflix.reactContext')+3
      final = dados.index('</script',comeco)-1
      if final>0:
        dado_json = dados[comeco:final]
    return json.loads(substituicoes(dado_json))

def iterar_valores(dicionarios):
    retorno = []
    for a in dicionarios:
        retorno = retorno + [a['value']]
    return '|'.join(retorno)

def inclui_dicionario(dicionario,vetor):
    if 'type' in vetor and 'data' in vetor and vetor['type']=='hero' and 'title' in vetor['data'] :
        dicionario.update({'titulo' : vetor['data']['title']})
    if 'type' in vetor and 'data' in vetor and vetor['type']=='moreDetails' and 'genres' in vetor['data'] :
        dicionario.update({'generos': iterar_valores(vetor['data']['genres'])})

def inclui_item_id(dicionario,urlnetflixitem):
    id_item = re.sub(r'.*/title/(\d+)/*',r'\1',urlnetflixitem)
    dicionario.update({'id':id_item})
        
def itera_json_item(urlnetflixitem, outra_vez=True):
    try :
        json_objeto = recupera_url_item(urlnetflixitem)
    except:
      print("Erro recuperando item na netflix: %s", urlnetflixitem)
      return None
    try:
        dados=json_objeto['models']['nmTitleUI']['data']['sectionData']
    except:
        if outra_vez:
            return itera_json_item(urlnetflixitem,False)
        print("Erro iterando objetos na netflix: %s, Netflix mudou sistema?", urlnetflixitem)
        return None
    try:
        dicionario = {}
        for a in dados:
            inclui_dicionario(dicionario,a)
        inclui_item_id(dicionario,urlnetflixitem)
        return dicionario
    except:
        print("Erro iterando dicionários, falha na programação?")
        return None

def recuperar_filmes(caminho_html):
    leitor = open(caminho_html,'r')
    texto = leitor.read()
    leitor.close()
    
    pattern = re.compile(r'"/title/(\d+)">([^<]+)<')
    objeto = []
    
    itens_por_t = 100
    numero_itens = len(re.findall(pattern, texto))
    numero_threads = int(numero_itens/itens_por_t)
    if numero_threads*itens_por_t < numero_itens:
        numero_threads = numero_threads + 1
    print('itens para avaliar: ', len(re.findall(pattern, texto)))
    print('numero de threads: ', numero_threads)
    print('itens por thread: ', itens_por_t)
    
    
    grupo_completo = []
    for (filmeid,nomeitem) in re.findall(pattern, texto):
        grupo_completo = grupo_completo + [ {filmeid:nomeitem}]
    
    threads = []
    manager = Manager()
    mapa = manager.dict()
    for i in range(numero_threads):
        inicio = i * itens_por_t
        fim = (i+1)*itens_por_t
        if fim > numero_itens:
            fim=numero_itens
        sub_grupo = grupo_completo[inicio:fim]
        mapa['conjunto-{}'.format(i)] = sub_grupo
        p = Process(target=processar_em_thread, args=(
                    mapa, i))
        time.sleep(10)
        p.start()
        threads = threads + [p]
    for t1 in threads:
        t1.join()
    
    retorno_final = []
    for i in range(len(mapa)):
        chave = 'conjunto-{}'.format(i)
        if chave in mapa:
            retorno_final = retorno_final + mapa[chave]
    
    print('feito!')
    return retorno_final

def processar_em_thread(mapa, tnum):
    #print(f'iniciando a thread {tnum}')
    if not mapa is None:
        mapa['t-{}'.format(tnum)] = 'ini'
    conjunto = mapa['conjunto-{}'.format(tnum)]
    i = 0
    objeto=[]
    for item_em_subgrupo in conjunto:
        for chave in item_em_subgrupo:
            (filmeid,nomeitem) = (chave , item_em_subgrupo[chave])
            time.sleep(random.randrange(5)+1)
            retorno = itera_json_item(f'https://www.netflix.com/br/title/{filmeid}')
            if retorno is not None:
                retorno.update({'nomeCompleto':nomeitem})
                objeto = objeto + [retorno]
            i=i+1
            mapa['q-{}'.format(tnum)] = i
    mapa['t-{}'.format(tnum)] = 'fim'
    mapa['conjunto-{}'.format(tnum)] = objeto
    estati = ''
    itens = 0
    abertas = 0
    for i in range(len(mapa)):
        chave = 't-{}'.format(i)
        chaveq = 'q-{}'.format(i)
        if chave in mapa:
            if mapa[chave] == 'ini':
                estati = estati + ' {}'.format(i)
                abertas = abertas + 1
        if chaveq in mapa:
            itens = itens + mapa[chaveq]
    if abertas > 20:
        estati = ' ... {} ao total ... '.format(abertas)
    if abertas > 0:
        print('{} itens lidos na netflix | threads abertas: {}'.format(itens, estati))
           
            
caminho_html = '/home/vpn/compartilhada/NetflixTotal.html'
vetor = recuperar_filmes(caminho_html)
po = pd.DataFrame(vetor)

po.to_csv('/home/vpn/compartilhada/NetflixTotal.pd')
print('feito!')
