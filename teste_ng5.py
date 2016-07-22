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
circuito = '''*TCR - Tyristor Controled Reactor

* .------------------------------.
* |      Parametros Gerais       |
* `------------------------------'
.param freq = 60
.param cond = 1 ; corrente de conducao minima
.param v_min = 1k

* .---------------------------------.
* | Descricao do circuito principal |
* `---------------------------------'
*Fonte de 18.5kV/60Hz ligada entre o n_sist1 e o GND
*condicao inicial  = 0V
vi n_fonte 0 dc 0 sin(0 26.163k freq 0 0)
*varia o angulo de disparo de 165 a 90
vang n_ang 0 dc 0 pwl(0 165 4 90)

xtcr1 n_fonte 0 n_ang tcr

amed1 %vnam(vi) i_rms med1

amed2 n_fonte %vnam(vi) tcr_p tcr_q med2

.model med1 rms(freq = {freq}, pontos = 32)
.model med2 vi_pq(freq = {freq}, pontos = 32)

* .---------------------------------------.
* |Subcircuito: TCR                       |
* |Modela um TCR completo monofasico      |
* `---------------------------------------'
.subckt tcr n_sist1 n_sist2 ang

*----Valvula----------------------------------
*tiristor semiciclo positivo
sgatep n_sist1 n_d_p gate 0 chave1 off ;chave que inicia a conducao -P
scorrp n_sist1 n_d_p nverp 0 chave1 off ;chave que sela a conducao - P
dp n_d_p nsensorp diodo1

vsensorp nsensorp n_carga 0

econdp nverp 0 value = {(i(vsensorp))>cond} ;avalia o modulo de corrente
rcondp nverp 0 1

*tiristor semiciclo negativo
sgaten n_sist1 n_d_n gate 0 chave1 off ;chave que inicia a conducao - N
scorrn n_sist1 n_d_n nvern 0 chave1 off ;chave que sela a conducao - N
dn nsensorn n_d_n diodo1

vsensorn nsensorn n_carga 0

econdn nvern 0 value = {(i(vsensorn))<-cond} ;avalia o modulo de corrente
rcondn nvern 0 1

rgate gate 0 10k

*--snuber-------------------------------------
rs n_sist1 n_snuber 1k
cs n_snuber n_carga 0.11u

*----resistencia de carga - paralelo ao indutor---------------
rpar n_carga n_sist2 100meg ;Resistor de 10mega ohms ligado entre o n_carga e o GND

*----indutor de carga----------------------------------------------
Lprinc n_carga n_perda 13.44m ;indutancia de 13.44mH
rperda n_perda n_sist2 0.011	;resistencia de 0.011 ohm em serie

*----circuito de controle-------------------------
adisp %vd(n_sist1 n_sist2) ang gate disparo

* .--------------------------.
* | Descricao de componentes |
* `--------------------------'

.model chave1 sw vt=0.5 ron=0.001 roff=10meg
.model chave2 sw vt=0.5 ron=30 roff=100k
.model diodo1 d IS=1e-14 n=1
.model disparo pfc(freq = {freq}, v_min = {v_min})

.ends

* .--------------------------------------.
* | Parametros de analise de Transitorio |
* `--------------------------------------'
*ATENCAO: Sempre considerar as condicoes iniciais (parametro uic)
*passo de amostragem = (360pts na freq atual), tempo total de 4s
.save all
.TRAN {1/(freq*360)} 4 uic

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
spice.plotar(['i_rms', ], '', 0)
spice.plotar(['tcr_p', 'tcr_q' ], '', 1)