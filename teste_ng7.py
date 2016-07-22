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
.param tensao = 707.107k
.param resist = 10
*.param relacao = 10

* .-----------------------.
* | Descricao do circuito |
* `-----------------------'

*Fontes (condicao inicial igual a zero)
Va pa 0 dc 0 sin(0 {tensao} {freq} 0 0 0)
Vb pb 0 dc 0 sin(0 {tensao} {freq} 0 0 -120)
Vc pc 0 dc 0 sin(0 {tensao} {freq} 0 0 120)

*Resistores na fonte para estabilidade
r1 pa 0 10k
r2 pb 0 10k
r3 pc 0 10k

*Resistores (carga equilibrada)
Ra sa neutro {resist}
Rb sb neutro {resist}
Rc sc neutro {resist}

*Transformadores (ligacao estrela-delta)
Xta pa 0 sa sb trafo
Xtb pb 0 sb sc trafo
Xtc pc 0 sc sa trafo

*teste
Xtt trafop 0 trafos 0 trafo
rt trafos 0 .20535
*vmed2 pa med dc 0 0
amed2 pa %id(pa trafop) tp tq med2

*medidor de indutancia
amed %vd(sa sb) l_med med_l

* .--------------------------.
* | Descricao de componentes |
* `--------------------------'
.model med_l lmeter
.model med2 vi_pq(freq = {freq}, pontos = 32)
* .---------------------------------------.
* |Subcircuito: Transformador             |
* `---------------------------------------'
* .----------------------------------------.
* |                                        |
* |      R1                       R2       |
* | P1   ___   node1      node2  ___    S1 |
* | o---|___|--o            o---|___|---o  |
* |            |            |              |
* |            |            |              |
* |            C|     K     C|             |
* |         L1 C| +-------+ C| L2          |
* |            C|           C|             |
* |            |            |              |
* | P2         |            |           S2 |
* | o----------'            '-----------o  |
* |                                        |
* '----------------------------------------'
.subckt trafo p1 p2 s1 s2
R1 p1 node1 0.1 ;resit primario = 0.1 ohm
R2 node2 s1 0.01 ;resit sec = 0.01 ohm
L1 node1 p2 1000 ;indutancia prim
L2 node2 s2 1.369 ;indut sec = (L1/(rel^2))

*fator de acoplamento entre as bobinas
*determina a ind de dispersao Ldisp = L*(1-K)
K L1 L2 0.99980104

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

'''spice.cmd('sec_a = sa - neutro')
spice.cmd('sec_b = sb - neutro')
spice.cmd('sec_c = sc - neutro')
spice.plotar(['pa', 'pb', 'pc', 'sec_a', 'sec_b', 'sec_c'], '', 0)
spice.plotar(['pa', 'sec_a'], '', 1)'''
spice.plotar(['tp', 'tq'],'',0)
spice.plotar(['l.xtt.l1#branch', ],'',1)