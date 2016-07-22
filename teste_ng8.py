import ngspyce.ngspyce as ng
import ngspyce.gui as ng_gui
import os

spice = ng.app()
janela = ng_gui.Janela(args=(spice,))

curr_dir_before = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/ngspyce/'
dir_cm = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/ngspyce/lib/ngspice/'
spice.cmd('cd ' + dir_cm)
spice.cmd('codemodel ./analog.cm')
spice.cmd('codemodel ./digital.cm')
spice.cmd('codemodel ./spice2poly.cm')
spice.cmd('codemodel ./xtradev.cm')
spice.cmd('codemodel ./xtraevt.cm')
spice.cmd('cd ' + curr_dir_before + '/teste_cm')

spice.cmd('codemodel ./teste.cm')
spice.cmd('cd ' + curr_dir_before)
circuito = '''*Transformador

* .------------------------------.
* |      Parametros Gerais       |
* `------------------------------'
.param freq = 60
.param tensao = {500k * sqrt(2/3)}
.param resist = 1
.param relacao = {tensao / 18.5k}

* .-----------------------.
* | Descricao do circuito |
* `-----------------------'

*Fontes (condicao inicial igual a zero)
Va pa 0 dc 0 sin(0 {tensao} {freq} 0 0 0)
Vb pb 0 dc 0 sin(0 {tensao} {freq} 0 0 -120)
Vc pc 0 dc 0 sin(0 {tensao} {freq} 0 0 120)


*Resistores (carga equilibrada)
Ra sa neutro {resist}
Rb sb neutro {resist}
Rc sc neutro {resist}

*Transformadores (ligacao estrela-delta)
Xta pa 0 sa sb trafo rel={1/relacao}
Xtb pb 0 sb sc trafo rel={1/relacao}
Xtc pc 0 sc sa trafo rel={1/relacao}

*teste
amed2 pa %id(pa indp) tp tq med2
ltp indp trafop 300m
Xtt trafop 0 trafos 0 trafo rel={1/relacao}
rt trafos 0 1
*lts inds 0 10u
vmed2 pa med dc 0 0

*medidor de indutancia
*amed %vd(sa sb) l_med med_l

* .--------------------------.
* | Descricao de componentes |
* `--------------------------'
*.model med_l lmeter
.model med2 vi_pq(freq = {freq}, pontos = 32)
* .---------------------------------------.
* |Subcircuito: Transformador             |
* `---------------------------------------'
.subckt trafo p1 p2 s1 s2 rel=1.0
g1 p1 p2 0 inter {rel}
g2 inter 0 s2 s1 1
g3 inter 0 p1 p2 {rel}
g4 s1 s2 inter 0 1
rinter inter 0 1g
.ends


* .--------------------------------------.
* | Parametros de analise de Transitorio |
* `--------------------------------------'

*passo de amostragem = (32pts na freq atual), tempo total de 35 ms
*ATENCAO: Sempre considerar as condicoes iniciais (parametro uic)
.TRAN {1/(freq*32)} 1 uic
* .--------------------------------------.
* |             ---- FIM ---             |
* `--------------------------------------'
.end
'''
verifica = spice.circ(circuito)
spice.cmd('bg_run')
with spice.ng_livre:
    while not spice.ng_n_exec:
	#print 'esperando'
	spice.ng_livre.wait()

spice.cmd('rusage time') #verifica o tempo total de simulacao
'''
spice.cmd('sec_a = sa - neutro')
spice.cmd('sec_b = sb - neutro')
spice.cmd('sec_c = sc - neutro')
spice.plotar(['pa', 'pb', 'pc', 'sec_a', 'sec_b', 'sec_c'], '', 2)
spice.plotar(['pa', 'sec_a'], '', 1)'''
spice.plotar(['tp', 'tq'],'',0)
#spice.plotar(['l.xtt.l1#branch', ],'',1)